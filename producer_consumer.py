import queue
import threading
import time
import traceback
import numpy as np
from PIL import Image, ImageFilter


class Task:
    def __init__(self, idx, strip, fname):
        self.idx = idx
        self.strip = strip
        self.fname = fname


class Result:
    def __init__(self, idx, data=None, err=None):
        self.idx = idx
        self.data = data
        self.err = err


def invert(arr):
    return 255 - arr


def blur(arr):
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.BoxBlur(5))
    return np.array(img)


def brightness(arr):
    tmp = arr.astype(np.float64) * 1.5
    tmp = np.clip(tmp, 0, 255)
    return tmp.astype(np.uint8)


FILTERS = {
    "invert": invert,
    "blur": blur,
    "brightness": brightness,
}


class Producer(threading.Thread):
    def __init__(self, image, fname, tq, nstrips, nconsumers, stop_ev):
        super().__init__(daemon=True)
        self.image = image
        self.fname = fname
        self.tq = tq
        self.nstrips = nstrips
        self.nconsumers = nconsumers
        self.stop_ev = stop_ev

    def run(self):
        h = self.image.shape[0]
        sh = h // self.nstrips

        for i in range(self.nstrips):
            if self.stop_ev.is_set():
                break
            y0 = i * sh
            y1 = h if i == self.nstrips - 1 else (i + 1) * sh
            strip = self.image[y0:y1].copy()
            self.tq.put(Task(i, strip, self.fname))

        for _ in range(self.nconsumers):
            self.tq.put(None)


class Consumer(threading.Thread):
    def __init__(self, tq, rq, stop_ev, cid):
        super().__init__(daemon=True)
        self.tq = tq
        self.rq = rq
        self.stop_ev = stop_ev
        self.name = f"Consumer-{cid}"

    def run(self):
        while not self.stop_ev.is_set():
            try:
                task = self.tq.get(timeout=0.1)
            except queue.Empty:
                continue

            if task is None:
                self.tq.task_done()
                break

            try:
                fn = FILTERS[task.fname]
                out = fn(task.strip)
                res = Result(task.idx, data=out)
            except Exception:
                res = Result(task.idx, err=traceback.format_exc())
                self.stop_ev.set()

            self.rq.put(res)
            self.tq.task_done()


class ImageProcessor:
    def __init__(self, image, fname, nconsumers=4):
        self.image = image
        self.fname = fname
        self.nconsumers = nconsumers
        self.nstrips = nconsumers * 2

    def process(self):
        tq = queue.Queue()
        rq = queue.Queue()
        stop_ev = threading.Event()

        prod = Producer(self.image, self.fname, tq, self.nstrips, self.nconsumers, stop_ev)
        consumers = [Consumer(tq, rq, stop_ev, i) for i in range(self.nconsumers)]

        prod.start()
        for c in consumers:
            c.start()

        prod.join()
        for c in consumers:
            c.join()

        results = []
        while not rq.empty():
            results.append(rq.get())

        errs = [r for r in results if r.err is not None]
        if errs:
            raise RuntimeError(f"ошибка в полосе {errs[0].idx}:\n{errs[0].err}")

        results.sort(key=lambda r: r.idx)
        return np.vstack([r.data for r in results])


def run_seq(image, fname):
    return FILTERS[fname](image)


def make_test_image(w=2000, h=2000):
    row = np.linspace(0, 255, w, dtype=np.uint8)
    col = np.linspace(0, 255, h, dtype=np.uint8)
    r = np.outer(col, np.ones(w, dtype=np.uint8))
    g = np.outer(np.ones(h, dtype=np.uint8), row)
    b = np.outer(255 - col, row // 2 + 128).astype(np.uint8)
    return np.stack([r, g, b], axis=2)


def main():
    print("Генерация тестового изображения...")
    img = make_test_image()
    print(f"Размер: {img.shape[1]}x{img.shape[0]}\n")

    for fname in ["invert", "blur", "brightness"]:
        print("=" * 55)
        print(f"Фильтр: {fname}")
        print("=" * 55)

        t0 = time.perf_counter()
        seq_res = run_seq(img, fname)
        seq_t = time.perf_counter() - t0

        Image.fromarray(seq_res).save(f"output_{fname}.png")
        print(f"  Последовательно: {seq_t:.4f} сек\n")
        print(f"  {'Consumers':<12} {'Время, с':<14} {'Ускорение':<12} {'Корректность'}")
        print(f"  {'-'*55}")

        for nc in [1, 2, 4, 8]:
            t0 = time.perf_counter()
            par_res = ImageProcessor(img, fname, nc).process()
            par_t = time.perf_counter() - t0

            spdup = seq_t / par_t if par_t > 0 else 0
            ok = "OK" if np.array_equal(seq_res, par_res) else "РАСХОЖДЕНИЕ"
            print(f"  {nc:<12} {par_t:<14.4f} {spdup:<12.2f} {ok}")

        Image.fromarray(par_res).save(f"output_{fname}_parallel.png")
        print()

    print("Готово!")


if __name__ == "__main__":
    main()
