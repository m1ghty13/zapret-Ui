"""System tray icon with menu for Zapret UI."""
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)


class TrayIcon:
    """System tray icon with context menu."""

    def __init__(self, runner, api_port):
        self.runner = runner
        self.api_port = api_port
        self.icon = None
        self.window = None

    def create_icon(self):
        """Create system tray icon."""
        try:
            import pystray
            from PIL import Image

            # Load icon
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                image = Image.open(str(icon_path))
            else:
                # Create simple icon if file not found
                image = Image.new('RGB', (64, 64), color='blue')

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem('Zapret UI', self._show_window, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('Статус', self._get_status_menu()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('Стратегии', self._get_strategies_menu()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    'Запустить',
                    self._start_protection,
                    visible=lambda item: not self.runner.is_running()
                ),
                pystray.MenuItem(
                    'Остановить',
                    self._stop_protection,
                    visible=lambda item: self.runner.is_running()
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('Открыть UI', self._show_window),
                pystray.MenuItem('Выход', self._quit_app)
            )

            self.icon = pystray.Icon(
                "zapret-ui",
                image,
                "Zapret UI",
                menu
            )

            return self.icon

        except ImportError:
            log.warning("pystray not installed, tray icon disabled")
            return None

    def _get_status_menu(self):
        """Get status submenu."""
        import pystray

        def get_status_text(item):
            if self.runner.is_running():
                strategy = self.runner.current_strategy()
                return f"✓ Активен ({strategy})"
            return "○ Неактивен"

        return pystray.MenuItem(
            get_status_text,
            lambda: None,
            enabled=False
        )

    def _get_strategies_menu(self):
        """Get strategies submenu."""
        import pystray
        import core.strategies as strats
        import core.config as cfg

        current = cfg.get("current_strategy", "ALT")

        items = []
        for name in strats.ALL_STRATEGIES[:10]:  # First 10 strategies
            items.append(
                pystray.MenuItem(
                    f"{'✓ ' if name == current else '  '}{name}",
                    lambda _, n=name: self._select_strategy(n)
                )
            )

        return pystray.Menu(*items)

    def _select_strategy(self, strategy_name):
        """Select strategy."""
        import core.config as cfg
        cfg.set("current_strategy", strategy_name)
        log.info(f"Strategy selected: {strategy_name}")

        # Restart if running
        if self.runner.is_running():
            self._stop_protection()
            import time
            time.sleep(1)
            self._start_protection()

    def _start_protection(self, icon=None, item=None):
        """Start protection."""
        import core.config as cfg
        import core.domains as domains_mod

        strategy = cfg.get("current_strategy", "ALT")
        enabled_groups = cfg.get("enabled_groups", [])
        hostlist_path = str(domains_mod.build_hostlist(enabled_groups))

        success = self.runner.start(strategy, hostlist_path)
        if success:
            log.info("Protection started from tray")
            if self.icon:
                self.icon.notify("Zapret UI", f"Защита запущена: {strategy}")
        else:
            log.error("Failed to start protection from tray")
            if self.icon:
                self.icon.notify("Zapret UI", "Ошибка запуска")

    def _stop_protection(self, icon=None, item=None):
        """Stop protection."""
        self.runner.stop()
        log.info("Protection stopped from tray")
        if self.icon:
            self.icon.notify("Zapret UI", "Защита остановлена")

    def _show_window(self, icon=None, item=None):
        """Show main window."""
        if self.window:
            try:
                self.window.show()
            except:
                pass
        else:
            # Open browser if window not available
            import webbrowser
            webbrowser.open(f"http://127.0.0.1:{self.api_port}")

    def _quit_app(self, icon=None, item=None):
        """Quit application."""
        log.info("Quitting from tray")

        # Stop protection
        if self.runner.is_running():
            self.runner.stop()

        # Stop icon
        if self.icon:
            self.icon.stop()

        # Exit
        sys.exit(0)

    def run(self):
        """Run tray icon (blocking)."""
        if self.icon:
            self.icon.run()

    def stop(self):
        """Stop tray icon."""
        if self.icon:
            self.icon.stop()
