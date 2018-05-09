import tensorflow as tf
import os
from object_detection.dataset_tools.create_coco_tf_record import _create_tf_record_from_coco_annotations

annotations_file = '/home/nathan/Visually-Impaired-Transport-Assistance/data/' \
                    'coco/annotations/instances_val2017.json'
image_dir = '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/images/val'
output_dir = '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/tfrecord'

def dataset2TFRecord(annotations_file, image_dir, output_dir,
                     output_name='train', include_mask=False):
    if not tf.gfile.IsDirectory(output_dir):
        tf.gfile.MakeDirs(output_dir)
    output_path = os.path.join(output_dir, output_name + '.record')

    _create_tf_record_from_coco_annotations(annotations_file,
                                            image_dir,
                                            output_path,
                                            include_mask)

dataset2TFRecord(annotations_file, image_dir, output_dir, 'val')


