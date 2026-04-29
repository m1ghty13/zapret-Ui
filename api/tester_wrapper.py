"""Non-Qt wrapper for StrategyTester."""
import logging
import time
import threading
from typing import Any
from queue import Queue

import httpx

import core.config as cfg
import core.strategies as strats
from api.runner_wrapper import FlaskRunner

log = logging.getLogger(__name__)

TEST_TIMEOUT = 5.0
SETTLE_TIME = 3.0


class FlaskTester:
    """Tests strategies without Qt dependencies."""

    def __init__(self, event_queue: Queue):
        self._event_queue = event_queue
        self._running = False
        self._thread: threading.Thread | None = None

    def run_async(self, strategies: list[str], domains: list[str]) -> None:
        """Start testing in background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run_tests,
            args=(strategies, domains),
            daemon=True
        )
        self._thread.start()

    def is_running(self) -> bool:
        """Check if test is running."""
        return self._running

    def _run_tests(self, strategies: list[str], domains: list[str]) -> None:
        """Run tests in background."""
        # Create a dummy log queue for the runner
        from queue import Queue
        dummy_log_queue = Queue()
        runner = FlaskRunner(dummy_log_queue)

        all_scores: dict[str, dict[str, Any]] = {}
        total = len(strategies)
        hostlist_path = cfg.get("hostlist_path", "lists/hostlist.txt")

        for idx, name in enumerate(strategies):
            percent = int(((idx + 1) / total) * 100)
            self._emit({
                "type": "progress",
                "strategy": name,
                "current": idx + 1,
                "total": total,
                "percent": percent
            })

            log.info("[Тест %d/%d] %s", idx + 1, total, name)

            ok = runner.start(name, hostlist_path)
            if not ok:
                all_scores[name] = {"score": 0, "total": len(domains), "status": "failed"}
                self._emit({
                    "type": "result",
                    "strategy": name,
                    "score": 0,
                    "total": len(domains),
                    "status": "failed"
                })
                continue

            time.sleep(SETTLE_TIME)

            score = self._test_domains(domains)
            runner.stop()
            time.sleep(0.5)

            total_domains = len(domains)
            if score == total_domains:
                status = "works"
            elif score > 0:
                status = "partial"
            else:
                status = "failed"

            all_scores[name] = {"score": score, "total": total_domains, "status": status}
            self._emit({
                "type": "result",
                "strategy": name,
                "score": score,
                "total": total_domains,
                "status": status
            })

        runner.stop()

        # Update config
        tested = cfg.get("tested_strategies", {})
        tested.update(all_scores)
        cfg.set("tested_strategies", tested)

        # Find best
        best = self._pick_best(all_scores)
        self._emit({
            "type": "done",
            "best": best,
            "scores": all_scores
        })

        self._running = False

    def _test_domains(self, domains: list[str]) -> int:
        """Test domains and return success count."""
        score = 0
        for domain in domains:
            url = f"https://{domain}"
            try:
                with httpx.Client(timeout=TEST_TIMEOUT, verify=False) as client:
                    resp = client.get(url, follow_redirects=True)
                if resp.status_code < 500:
                    score += 1
                    log.debug("  ✓ %s (%d)", domain, resp.status_code)
            except Exception as e:
                log.debug("  ✗ %s: %s", domain, e)
        return score

    @staticmethod
    def _pick_best(scores: dict[str, dict[str, Any]]) -> str:
        """Return strategy with highest score."""
        if not scores:
            return ""
        return max(scores, key=lambda n: scores[n].get("score", 0))

    def _emit(self, event: dict) -> None:
        """Emit event to queue."""
        try:
            self._event_queue.put_nowait(event)
        except:
            pass
