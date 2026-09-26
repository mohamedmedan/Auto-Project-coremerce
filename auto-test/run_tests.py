#!/usr/bin/env python3
"""Coremerce Feature-Based Test Suite - Interactive Runner"""
import argparse, json, os, sys, time
from datetime import datetime
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_factory import create_driver
from utils.reporter import ReportGenerator
from tests.base_test import SkipTest
from tests.registry import (
    FEATURES, list_features, get_tests_by_feature, get_tests_by_keys,
)

ROOT = Path(__file__).resolve().parent


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    CYAN = "\033[96m"; MAGENTA = "\033[95m"


def _ansi():
    if os.name == "nt":
        try:
            import colorama; colorama.just_fix_windows_console()
        except ImportError:
            os.system("")


_ansi()


def load_config(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def banner():
    print(f"{C.CYAN}{C.BOLD}+===========================================================+")
    print("|        Coremerce Selenium Test Suite Runner               |")
    print(f"+===========================================================+{C.RESET}")


def print_tests(feature):
    feats = list_features() if feature == "all" else [feature]
    total = 0
    for feat in feats:
        tests = FEATURES.get(feat, [])
        print(f"\n{C.BOLD}{C.MAGENTA}>> {feat.upper()}{C.RESET} {C.DIM}({len(tests)}){C.RESET}")
        for cls in tests:
            print(f"  {C.GREEN}{cls.key:<14}{C.RESET} {C.DIM}[{cls.category:<12}]{C.RESET} {cls.name}")
        total += len(tests)
    print(f"\n{C.BOLD}Total: {total}{C.RESET}\n")


def ask(p, default=""):
    s = f" {C.DIM}[{default}]{C.RESET}" if default else ""
    try:
        return input(f"{C.BOLD}{p}{C.RESET}{s}: ").strip() or default
    except (EOFError, KeyboardInterrupt):
        print(); sys.exit(0)


def ask_yn(p, default=False):
    return ask(f"{p} (y/n)", "y" if default else "n").lower().startswith("y")


def ask_ch(p, valid):
    while True:
        a = ask(p).lower()
        if a in valid: return a
        print(f"{C.RED}x Invalid.{C.RESET}")


def run_one(cls, config, browser, headless, shots, rep):
    driver = None
    r = {"feature": getattr(cls, "feature", "?"), "key": cls.key,
         "name": cls.name, "description": cls.description,
         "category": cls.category, "status": "ERROR",
         "message": "", "duration": 0.0, "screenshot": None}
    try:
        driver = create_driver(browser=browser, headless=headless,
                               implicit_wait=config.get("implicit_wait", 5))
        wait = WebDriverWait(driver, config.get("timeout", 15))
        t = cls(driver, config, wait); t.setup()
        s = time.time()
        try:
            t.execute(); r["status"] = "PASSED"; r["message"] = "OK"
        except SkipTest as e:
            r["status"] = "SKIPPED"; r["message"] = f"Skipped: {e}"
        except AssertionError as e:
            r["status"] = "FAILED"; r["message"] = f"AssertionError: {e}"
        except Exception as e:
            r["status"] = "ERROR"; r["message"] = f"{type(e).__name__}: {e}"
        finally:
            r["duration"] = round(time.time() - s, 2)
        if r["status"] in ("FAILED", "ERROR"):
            try:
                os.makedirs(shots, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fn = f"{cls.key}_{ts}.png"
                full = os.path.join(shots, fn)
                driver.save_screenshot(full)
                r["screenshot"] = os.path.relpath(full, rep).replace("\\", "/")
            except Exception:
                pass
        try:
            t.teardown()
        except Exception:
            pass
    except Exception as e:
        r["status"] = "ERROR"; r["message"] = f"Setup: {type(e).__name__}: {e}"
    finally:
        if driver:
            try: driver.quit()
            except Exception: pass
    return r


def run_suite(tests, config, browser, headless, label):
    rep = ROOT / config.get("report_dir", "reports")
    shots = ROOT / config.get("screenshots_dir", "reports/screenshots")
    rep.mkdir(parents=True, exist_ok=True)
    print(f"\n{C.BOLD}{C.CYAN}>> {len(tests)} tests | feature={label} | browser={browser} | headless={headless}{C.RESET}\n")
    results = []
    for cls in tests:
        print(f"  > {cls.key:<14} {cls.name[:55]:<55}", end="", flush=True)
        r = run_one(cls, config, browser, headless, str(shots), str(rep))
        results.append(r)
        icons = {"PASSED": f"{C.GREEN}PASS{C.RESET}", "FAILED": f"{C.RED}FAIL{C.RESET}",
                 "ERROR": f"{C.YELLOW}ERR {C.RESET}", "SKIPPED": f"{C.DIM}SKIP{C.RESET}"}
        print(f"{icons.get(r['status'], r['status'])} ({r['duration']}s)")
    safe = label.replace(",", "_")[:40]
    rp = rep / f"report_{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    ReportGenerator(config, results, str(rp)).generate()
    p = sum(1 for r in results if r["status"] == "PASSED")
    f = sum(1 for r in results if r["status"] == "FAILED")
    e = sum(1 for r in results if r["status"] == "ERROR")
    s = sum(1 for r in results if r["status"] == "SKIPPED")
    color = C.GREEN if (f == 0 and e == 0) else C.RED
    print(f"\n{color}{C.BOLD}Summary:{C.RESET} {len(results)} | "
          f"{C.GREEN}P:{p}{C.RESET} {C.RED}F:{f}{C.RESET} "
          f"{C.YELLOW}E:{e}{C.RESET} {C.DIM}S:{s}{C.RESET}")
    print(f"Report: {C.CYAN}{rp}{C.RESET}\n")
    return 0 if (f == 0 and e == 0) else 1


def interactive(cfg_path):
    config = load_config(cfg_path)
    while True:
        banner()
        feats = list_features()
        print(f"{C.BOLD}Main Menu:{C.RESET}\n")
        for i, feat in enumerate(feats, 1):
            print(f"  {C.CYAN}{i}{C.RESET}) {C.BOLD}{feat.title()}{C.RESET} {C.DIM}({len(FEATURES[feat])}){C.RESET}")
        n = len(feats)
        print(f"  {C.CYAN}{n+1}{C.RESET}) {C.BOLD}All Features{C.RESET}")
        print(f"  {C.CYAN}{n+2}{C.RESET}) {C.BOLD}Custom Keys{C.RESET}")
        print(f"  {C.CYAN}{n+3}{C.RESET}) {C.BOLD}List Tests{C.RESET}")
        print(f"  {C.CYAN}0{C.RESET}) {C.BOLD}Exit{C.RESET}\n")
        ch = ask_ch("Select", {str(i) for i in range(0, n + 4)})
        if ch == "0":
            print(f"\n{C.DIM}Bye{C.RESET}\n"); return 0
        if ch == str(n + 3):
            print(); print_tests("all"); ask("Press Enter", ""); continue
        if ch == str(n + 2):
            ki = ask("Keys (comma-separated)")
            keys = [k.strip() for k in ki.split(",") if k.strip()]
            tests = get_tests_by_keys(keys, "all")
            if not tests:
                print(f"{C.RED}No match.{C.RESET}\n"); continue
            for cls in tests: print(f"   - {cls.key:<14} {cls.name}")
            if not ask_yn("Proceed?", True): continue
            label = "custom"
        elif ch == str(n + 1):
            browser = ask_ch("Browser (chrome/firefox/edge)", {"chrome", "firefox", "edge"})
            headless = ask_yn("Headless?", False)
            return run_suite(get_tests_by_feature("all"), config, browser, headless, "all")
        else:
            feature = feats[int(ch) - 1]
            print(f"\n{C.BOLD}{feature}{C.RESET}: 1) All  2) Pick keys")
            sub = ask_ch("Select", {"1", "2"})
            if sub == "1":
                tests = get_tests_by_feature(feature)
            else:
                for cls in FEATURES[feature]:
                    print(f"   - {C.GREEN}{cls.key}{C.RESET}  {cls.name}")
                ki = ask("Keys (comma-separated)")
                keys = [k.strip() for k in ki.split(",") if k.strip()]
                tests = get_tests_by_keys(keys, feature)
                if not tests:
                    print(f"{C.RED}No match.{C.RESET}\n"); continue
            browser = ask_ch("Browser (chrome/firefox/edge)", {"chrome", "firefox", "edge"})
            headless = ask_yn("Headless?", False)
            label = feature
        return run_suite(tests, config, browser, headless, label)


def cli():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--feature", default=None)
    p.add_argument("--keys", default=None)
    p.add_argument("--list", action="store_true")
    p.add_argument("--config", default=str(ROOT / "config" / "config.json"))
    p.add_argument("--browser", choices=["chrome", "firefox", "edge"], default=None)
    p.add_argument("--headless", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    a = p.parse_known_args()[0]
    if a.help:
        print(__doc__); return 0
    if not (a.feature or a.keys or a.list):
        return interactive(a.config)
    config = load_config(a.config)
    if a.list:
        print_tests(a.feature or "all"); return 0
    feat = (a.feature or "all").lower()
    if feat != "all" and feat not in FEATURES:
        print(f"Unknown feature: {feat}"); return 2
    if a.keys:
        keys = [k.strip() for k in a.keys.split(",") if k.strip()]
        tests = get_tests_by_keys(keys, feat)
    else:
        tests = get_tests_by_feature(feat)
    if not tests:
        print("No tests"); return 2
    b = a.browser or config.get("browser", "chrome")
    h = a.headless or bool(config.get("headless", False))
    return run_suite(tests, config, b, h, feat)


if __name__ == "__main__":
    sys.exit(cli())
