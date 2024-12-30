import pytest
from datetime import datetime, timedelta
from polar_h10.data_quality import DataQuality

class TestDataQuality:
    """Test suite for DataQuality class."""
    
    @pytest.fixture
    def quality_monitor(self):
        return DataQuality(buffer_size=10)
    
    def test_initialization(self, quality_monitor):
        """Test initial state of DataQuality."""
        assert quality_monitor.signal_quality == 100.0
        assert quality_monitor.data_gaps == 0 
        assert quality_monitor.anomalies == 0
        assert len(quality_monitor.buffer) == 0
    
    def test_normal_heart_rate(self, quality_monitor):
        """Test quality calculation for normal heart rate."""
        now = datetime.now()
        quality_monitor.add_reading(now, 75)  # Normal heart rate
        stats = quality_monitor.get_stats()
        assert stats['signal_quality'] == 100.0
        assert stats['anomalies'] == 0
        
    def test_anomalous_heart_rate(self, quality_monitor):
        """Test quality calculation for anomalous heart rate.""" 
        now = datetime.now()
        quality_monitor.add_reading(now, 250)  # Above normal range
        stats = quality_monitor.get_stats()
        assert stats['signal_quality'] < 100.0
        assert stats['anomalies'] == 1
        
    def test_data_gap_detection(self, quality_monitor):
        """Test detection of data gaps."""
        now = datetime.now()
        quality_monitor.add_reading(now, 75)
        quality_monitor.add_reading(now + timedelta(seconds=2), 76)  # 2-second gap
        stats = quality_monitor.get_stats()
        assert stats['data_gaps'] == 1
        assert stats['signal_quality'] < 100.0
        
    def test_sudden_change_detection(self, quality_monitor):
        """Test detection of sudden heart rate changes."""
        now = datetime.now()
        quality_monitor.add_reading(now, 60)
        quality_monitor.add_reading(now + timedelta(seconds=1), 100)  # Sudden increase
        stats = quality_monitor.get_stats()
        assert stats['anomalies'] == 1
        assert stats['signal_quality'] < 100.0
        
    def test_buffer_size_limit(self, quality_monitor):
        """Test buffer size limit enforcement."""
        now = datetime.now()
        for i in range(15):  # Buffer size is 10
            quality_monitor.add_reading(now + timedelta(seconds=i), 75)
        assert len(quality_monitor.buffer) == 10
        
    def test_clear_data(self, quality_monitor):
        """Test clearing of all data."""
        now = datetime.now()
        quality_monitor.add_reading(now, 75)
        quality_monitor.clear()
        assert quality_monitor.signal_quality == 100.0
        assert quality_monitor.data_gaps == 0
        assert quality_monitor.anomalies == 0
        assert len(quality_monitor.buffer) == 0

