import unittest
import pandas as pd
from datetime import datetime, timedelta, timezone

from technical_analysis import analyze_golden_cross_state
from notifications import should_send_notification


def _build_df(sma50_values, sma128_values, closes=None):
    closes = closes or sma50_values
    index = pd.date_range("2024-01-01", periods=len(sma50_values), freq="H")
    return pd.DataFrame({
        'Close': closes,
        'SMA50': sma50_values,
        'SMA128': sma128_values
    }, index=index)


class SignalAnalysisTests(unittest.TestCase):
    def test_analyze_detects_fresh_golden_cross(self):
        df = _build_df(
            sma50_values=[95, 105],
            sma128_values=[100, 100],
            closes=[100, 106]
        )
        result = analyze_golden_cross_state(df, near_cross_threshold_pct=0.8)
        self.assertEqual(result['state'], 'golden')
        self.assertTrue(result['is_fresh_cross'])
    
    def test_analyze_identifies_near_cross_when_spread_tight(self):
        df = _build_df(
            sma50_values=[100, 101],
            sma128_values=[102, 102],
            closes=[101, 102]
        )
        result = analyze_golden_cross_state(df, near_cross_threshold_pct=1.5)
        self.assertEqual(result['state'], 'near')
        self.assertFalse(result['is_fresh_cross'])
    
    def test_should_send_notification_respects_cooldown_window(self):
        current = {
            'state': 'golden',
            'is_fresh_cross': False,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        now_iso = datetime.now(timezone.utc).isoformat()
        previous = {
            'state': 'golden',
            'is_fresh_cross': False,
            'last_notified_at': now_iso
        }
        self.assertFalse(should_send_notification(previous, current, cooldown_hours=12))
        
        old_time = (datetime.now(timezone.utc) - timedelta(hours=13)).isoformat()
        previous['last_notified_at'] = old_time
        self.assertTrue(should_send_notification(previous, current, cooldown_hours=12))


if __name__ == '__main__':
    unittest.main()
