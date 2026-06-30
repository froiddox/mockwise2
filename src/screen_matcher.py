import cv2
import numpy as np
import pyautogui


CONFIDENCE_THRESHOLD = 0.8

# Scale factors to try — covers common Windows DPI settings (100 % – 200 %)
# and small rendering differences in either direction.
_SCALES = [1.0, 0.75, 0.5, 1.25, 1.5, 1.75, 2.0, 0.9, 1.1]


def _count_distinct_matches(
    result: np.ndarray,
    threshold: float,
    template_h: int,
    template_w: int,
) -> int:
    """
    Count distinct matches above threshold.
    After each match found, suppress a region the size of the template around
    it so nearby pixels are not counted as a second match.
    Stops counting at 2 — caller only needs to know if there is more than one.
    """
    work = result.copy()
    count = 0
    while count < 2:
        _, max_val, _, max_loc = cv2.minMaxLoc(work)
        if max_val < threshold:
            break
        count += 1
        x, y = max_loc
        work[
            max(0, y - template_h // 2): y + template_h,
            max(0, x - template_w // 2): x + template_w,
        ] = 0.0
    return count


def find_reference_on_screen(image_path: str) -> tuple[tuple[int, int], float]:
    """
    Locate the reference image on the live screen using multi-scale OpenCV
    template matching.  Tries several scale factors to handle DPI differences
    between where the reference image was captured and the current display.
    Returns ((x, y), confidence) of the best match.
    Raises RuntimeError if not found or if multiple occurrences are detected.
    """
    screenshot = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    sh, sw = screen_gray.shape

    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise RuntimeError(f"Cannot read reference image: {image_path}")

    th, tw = template.shape
    best_val = 0.0
    best_loc: tuple[int, int] = (0, 0)
    best_result: np.ndarray | None = None
    best_scaled_h = th
    best_scaled_w = tw

    for scale in _SCALES:
        new_w = max(1, int(tw * scale))
        new_h = max(1, int(th * scale))

        if new_h >= sh or new_w >= sw:
            continue  # scaled template larger than screen — skip

        resized = cv2.resize(template, (new_w, new_h))
        result = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val_s, _, max_loc_s = cv2.minMaxLoc(result)

        if max_val_s > best_val:
            best_val = max_val_s
            best_loc = max_loc_s
            best_result = result
            best_scaled_h = new_h
            best_scaled_w = new_w

    if best_val < CONFIDENCE_THRESHOLD:
        raise RuntimeError(
            f"Reference image not found on screen "
            f"(best confidence {best_val:.2f} < {CONFIDENCE_THRESHOLD}). "
            "Ensure the target application is open and visible."
        )

    # Guard against multiple occurrences at the winning scale
    matches = _count_distinct_matches(
        best_result, CONFIDENCE_THRESHOLD, best_scaled_h, best_scaled_w
    )
    if matches > 1:
        raise RuntimeError(
            "Multiple occurrences of the reference image found on screen. "
            "Close duplicate windows and ensure only one instance is visible."
        )

    return best_loc, best_val  # (x, y) top-left corner, confidence score
