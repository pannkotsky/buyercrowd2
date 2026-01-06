from unittest.mock import MagicMock, patch

from app.scripts.backend_pre_start import init, logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    exec_mock = MagicMock(return_value=True)
    session_mock.configure_mock(**{"exec.return_value": exec_mock})
    # Make session_mock a context manager
    session_mock.__enter__ = MagicMock(return_value=session_mock)
    session_mock.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.scripts.backend_pre_start.Session", return_value=session_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        # Verify exec was called once
        session_mock.exec.assert_called_once()
        # Verify it was called with a select(1) statement
        # We can't use assert_called_once_with(select(1)) because select(1) creates
        # a new object each time, so we check the call args manually
        call_args = session_mock.exec.call_args[0]
        assert len(call_args) == 1, "exec should be called with one argument"
        # Verify the argument is a select statement that compiles to SELECT 1
        select_stmt = call_args[0]
        compiled = select_stmt.compile(compile_kwargs={"literal_binds": True})
        assert "1" in str(compiled), "exec should be called with select(1)"
