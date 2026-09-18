"""Test attribute selectors."""
from .. import util
import signal
import time
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_no_hang(self, pattern, timeout=3):
        """Assert the selector fails with a syntax error and does not hang the regular expression engine."""

        # `SIGALRM` is only available on Unix like systems, so interrupt the hang where we can,
        # and fall back to timing the operation everywhere else (Windows).
        if hasattr(signal, 'SIGALRM'):
            def timeout_handler(signum, frame):
                """Raise a timeout error when the alarm fires."""

                raise TimeoutError

            original = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            passed = False
            try:
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile(pattern)
                passed = True
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original)
            self.assertTrue(passed)
        else:
            start = time.perf_counter()
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(pattern)
            self.assertLess(time.perf_counter() - start, timeout)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_hang('[a="' + ('x' * 300))

    def test_bad_attribute_unclused_single_quote(self):
        """Test bad attribute with an unclosed single quote fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_hang("[a='" + ('x' * 300))

    def test_bad_contains_unclused(self):
        """Test bad `:-soup-contains` value fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_hang(':-soup-contains("' + ('x' * 300))

    def test_bad_lang_unclused(self):
        """Test bad `:lang` value fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_hang(':lang("' + ('x' * 300))

    def test_attribute_quoted_value_still_matches(self):
        """Test that quoted attribute values, including escapes, still parse and match."""

        self.assert_selector(
            self.MARKUP,
            'body [href="http://google.com"]',
            ["2"],
            flags=util.HTML5
        )

        self.assert_selector(
            self.MARKUP,
            "body [href='http://google.\\63 om']",
            ["2"],
            flags=util.HTML5
        )
