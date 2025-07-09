# Configuration settings

CONFIG = {
    'camera_resolution': '1280x720',
    'camera_fps': 30,
    'exposure': {
        'd435i': 150,
        'zed2i': 100,
    },
    'zed': {
        'enable_self_calibration': False,
        'depth_mode': 'PERFORMANCE',
        'depth_stabilization': True,
        'depth_minimum_distance': 200,
    },
    'dataset_root_dir': '../the-dataset',
    'directory_format': '{date}/{lighting}/{background_id}',
    'log_level': 'INFO',
    'log_file': 'multicam_collector.log',
}
