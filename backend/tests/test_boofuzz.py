import pytest
import asyncio
import socket
import threading
from app.plugins.base import ToolInput

# We can safely test if it fails loud when unavailable, but we assume it's available here since we just installed it.
from app.plugins.boofuzz_fuzzer import BoofuzzGuruxPlugin, BOOFUZZ_AVAILABLE, GURUX_AVAILABLE


# Mock a minimal DLMS/COSEM TCP server for testing
class MockDLMSServer:
    def __init__(self, host="127.0.0.1", port=4059):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        if self.thread:
            self.thread.join(timeout=1)

    def _run(self):
        try:
            while self.running:
                self.sock.settimeout(1.0)
                try:
                    conn, addr = self.sock.accept()
                except socket.timeout:
                    continue
                except Exception:
                    break

                with conn:
                    conn.settimeout(1.0)
                    try:
                        while self.running:
                            data = conn.recv(1024)
                            if not data:
                                break
                            
                            # Just a dumb server: respond to any request with some bytes
                            # A real DLMS UA response or AARE would have specific framing,
                            # but for the plugin test, any reply makes it proceed to the next step.
                            conn.sendall(b"\x00\x01\x00\x01\x00\x10\x00\x40UA_ACK_MOCK_RESPONSE")
                    except Exception:
                        pass
        except Exception:
            pass


@pytest.mark.skipif(not BOOFUZZ_AVAILABLE or not GURUX_AVAILABLE, reason="Dependencies not installed")
def test_boofuzz_gurux_plugin_execution():
    server = MockDLMSServer()
    server.start()
    
    try:
        plugin = BoofuzzGuruxPlugin()
        tool_input = ToolInput(
            target_filepath="dummy.bin",
            extra_args={"target_ip": "127.0.0.1", "target_port": 4059}
        )
        
        result = asyncio.run(plugin.execute_real(tool_input))
        
        assert result.success is True
        assert result.parsed_metrics is not None
        
        metrics = result.parsed_metrics
        assert "gurux_conformance" in metrics
        if not metrics["gurux_conformance"]["association_success"]:
            print("Gurux Error Details:", metrics["gurux_conformance"]["details"])
        assert metrics["gurux_conformance"]["association_success"] is True
        assert metrics["gurux_conformance"]["obis_read_success"] is True
        
        # Boofuzz bounded run should hit its limit
        assert metrics["fuzzed_messages"] > 0
        
        # Check logs
        log_str = "\n".join(result.logs)
        assert "[Gurux] Association successful." in log_str
        assert "[Gurux] OBIS read successful." in log_str
        assert "[Boofuzz] Bounded fuzzing limit reached" in log_str
    finally:
        server.stop()
