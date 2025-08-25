import os
import signal
import sys
import threading
import time

from src import Config, IRCLine, ModuleManager, utils

class Module(ModuleManager.BaseModule):
    def on_load(self):
        self._exited = False
        setattr(self.bot, "_shutting_down", False)

        signal.signal(signal.SIGINT, self.SIGINT)
        signal.signal(signal.SIGTERM, self.SIGINT)
        signal.signal(signal.SIGUSR1, self.SIGUSR1)
        signal.signal(signal.SIGHUP, self.SIGHUP)

    def SIGINT(self, signum, frame):
        print()
        setattr(self.bot, "_shutting_down", True)
        self.bot.trigger(lambda: self._kill(signum))

    def _kill(self, signum):
        if self._exited:
            return
        self._exited = True

        self.events.on("signal.interrupt").call(signum=signum)

        wrote_quit = False

        for server in list(self.bot.servers.values()):
            try:
                if getattr(server, "connected", False):
                    if hasattr(server, "socket") and hasattr(server.socket, "clear_send_buffer"):
                        server.socket.clear_send_buffer()

                    line = IRCLine.ParsedLine("QUIT", ["Shutting down"])
                    sent_line = server.send(line, immediate=True)
                    sent_line.events.on("send").hook(self._make_hook(server))

                    setattr(server, "send_enabled", False)
                    wrote_quit = True
                else:
                    self._safe_disconnect(server)
            except Exception:
                self._safe_disconnect(server)

        if not wrote_quit:
            sys.exit(0)

        def _failsafe():
            time.sleep(2.0)
            os._exit(0)

        t = threading.Thread(target=_failsafe, daemon=True)
        t.start()

    def _make_hook(self, server):
        return lambda e: self._disconnect_hook(server)

    def _disconnect_hook(self, server):
        self._safe_disconnect(server)
        if not self.bot.servers:
            sys.exit(0)

    def _safe_disconnect(self, server):
        try:
            self.bot.disconnect(server)
        except Exception:
            pass

    def SIGUSR1(self, signum, frame):
        self.bot.trigger(self._reload_config)

    def SIGHUP(self, signum, frame):
        self.bot.trigger(self._SIGHUP)

    def _SIGHUP(self):
        self._reload_config()
        self._reload_modules()

    def _reload_config(self):
        self.bot.log.info("Reloading config file")
        self.bot.config.load()
        self.bot.log.info("Reloaded config file")

    def _reload_modules(self):
        self.bot.log.info("Reloading modules")
        result = self.bot.try_reload_modules()
        if result.success:
            self.bot.log.info(result.message)
        else:
            self.bot.log.warn(result.message)
