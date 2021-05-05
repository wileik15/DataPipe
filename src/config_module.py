import json


class input_storage:

    config_dict = {
                    'camera': {
                        'wrld2cam_pose_list':[],
                        'is_structured_light': False

                    },
                    'projector': {
                        "proj2cam_pose": []
                    }
    }

    @classmethod
    def reset_config_dict(cls):

        cls.config_dict = {
                            'camera': {
                                'wrld2cam_pose_list':[],
                                'is_structured_light': False

                            },
                            'projector': {
                                "proj2cam_pose": []
                            }
            }