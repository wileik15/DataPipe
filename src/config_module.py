

class input_storage:

    config_dict = {
                    'camera': {
                        'wrld2cam_pose_list':[],
                        'focal_length': 50,
                        'sensor_width': 36,
                        'resolution': [480, 720],
                        'is_structured_light': False

                    },
                    'projector': {
                        'proj2cam_pose': [],
                        'focal_length': 50,
                        'sensor_width': 36,
                        'resolution': [480, 720]
                    },
                    'scene': {
                        'num_renders': 1,
                        'max_renders_per_scene': 1,
                        'min_renders_per_scene': 1,

                    },
                    'objects': {
                        'objects_list':[]

                    }

    }

    @classmethod
    def reset_config_dict(cls):
        """
        Resets configuration dict for the full pipeline.
        """

        cls.config_dict = {
                            'camera': {
                                'wrld2cam_pose_list':[],
                                'focal_length': 50,
                                'sensor_width': 36,
                                'resolution': [480, 720],
                                'is_structured_light': False

                            },
                            'projector': {
                                'proj2cam_pose': [],
                                'focal_length': 50,
                                'sensor_width': 36,
                                'resolution': [480, 720]
                            },
                            'scene': {
                                'num_renders': 1,
                                'max_renders_per_scene': 1

                            },
                            'objects': {
                                'objects_list':[]

                            }

            }