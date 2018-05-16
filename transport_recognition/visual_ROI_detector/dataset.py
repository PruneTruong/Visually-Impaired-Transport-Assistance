import tensorflow as tf
import numpy as np
import os
import csv
from object_detection.dataset_tools.create_coco_tf_record import _create_tf_record_from_coco_annotations
from object_detection.utils import dataset_util
from PIL import Image



annotations_file = '/home/nathan/Visually-Impaired-Transport-Assistance/data/' \
                    'coco/annotations/instances_val2017.json'
image_dir = '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/images/val'
output_dir = '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/tfrecord'

sample_config = {
    'img_dir': '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/images/dataset_val',
    'annotations_dir':'/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/annotations',
    'output_dir': '/home/nathan/Visually-Impaired-Transport-Assistance/data/coco/tfrecord_beta',
    'output_file_name': 'eval',
    'file_list_to_include': ['label.csv']

    }

def dataset2TFRecord(annotations_file, image_dir, output_dir,
                     output_name='train', include_mask=False):
    if not tf.gfile.IsDirectory(output_dir):
        tf.gfile.MakeDirs(output_dir)
    output_path = os.path.join(output_dir, output_name + '.record')
    _create_tf_record_from_coco_annotations(annotations_file,
                                            image_dir,
                                            output_path,
                                            include_mask)

#dataset2TFRecord(annotations_file, image_dir, output_dir, 'val')

def find_csv_filenames(path_to_dir, suffix=".csv" ):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

#def create_custom_dataset(dataset_config, data_dir, output_dir, output):



def create_1_tf_record(img_bits, annotation):
    # note : elements 0 are chosen for values that are the same for all annotations of this image
    height = int(annotation['height'][0])
    width = int(annotation['width'][0])
    filename = str.encode(annotation['img_name'][0])
    encoded_image_data = img_bits
    img_format = str.encode(annotation['img_format'])
    xmins = np.divide(np.array(annotation['x_min']).astype(np.float),
                      np.array(annotation['width']).astype(np.float))
    xmaxs = np.divide(np.array(annotation['x_max']).astype(np.float),
                      np.array(annotation['width']).astype(np.float))
    ymins = np.divide(np.array(annotation['y_min']).astype(np.float),
                      np.array(annotation['height']).astype(np.float))
    ymaxs = np.divide(np.array(annotation['y_max']).astype(np.float),
                      np.array(annotation['height']).astype(np.float))
    classes_text = [str.encode(categ) for categ in annotation['category']]
    classes = map(int, annotation['category_idx'])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image_data),
        'image/format': dataset_util.bytes_feature(img_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins.tolist()),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs.tolist()),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins.tolist()),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs.tolist()),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example
def retrieve_annotations(annotations_files, config):

def main(config):
    required = ['img_dir', 'output_dir', 'output_file_name', 'annotations_dir']
    for r in required:
        assert r in config
    output_path = config['output_dir'] + '/' + config['output_file_name'] + '.record'

    if not os.path.exists(output_path):
        if not tf.gfile.IsDirectory(config['output_dir']):
            tf.gfile.MakeDirs(config['output_dir'])
        with open(output_path, 'w'): pass

    writer = tf.python_io.TFRecordWriter(output_path)

    files_to_include = config.get('file_list_to_include', None)

    annotation_files = find_csv_filenames(config['annotations_dir'])
    annotations = []
    nb_ann = 0
    nb_img_tf_record = 0
    tf.logging.debug('Annotations files found in directory: {}' .format(annotation_files))

    #retrieve annotations and concatenate annotations for each image in a list of dicts
    annotations = retrieve_annotations(annotation_files, config)
    for file in annotation_files:
        if files_to_include is None or file in files_to_include:
            tf.logging.info('Reading file {} ...'.format(file))
            with open(config['annotations_dir'] + '/' + file) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    annotation = dict(row)
                    found_annotation = False

                    for existing_ann in annotations:
                        if annotation['img_name'] in existing_ann['img_name']:
                            found_annotation = True
                            for key, value in existing_ann.items():
                                existing_ann[key].append(annotation[key])
                            continue

                    if not found_annotation:
                        for key, value in annotation.items():
                            annotation[key] = [value]
                        annotations.append(annotation)

                    nb_ann = nb_ann + 1

    tf.logging.info(' Found {} images with a total of {} annotations' .format(len(annotations), nb_ann))

    # create tf record for each image
    for i in range(len(annotations)):
        # retrieve image from first element of list 'img_name'
        # note: all elements of the list are the same for that field
        try:
            annotations[i]['img_format'] = config.get('img_format', 'jpg')
            path_to_img = config['img_dir'] + '/' + annotations[i]['img_name'][0] + '.' + \
                          annotations[i]['img_format']
            with open(path_to_img, "rb") as img:
                tf_record = create_1_tf_record(img.read(), annotations[i])

            writer.write(tf_record.SerializeToString())
            nb_img_tf_record = nb_img_tf_record + 1

        except FileNotFoundError:
            tf.logging.warning(' Could not find image {} in img_dir. ' \
                            ' This image and corresponding annotations will'  \
                            ' not be added to the tf_record file.' .format(annotations[i]['img_name'][0]))

    writer.close()
    tf.logging.info(' Successfully created annotated tf_record dataset with {} images.' .format(nb_img_tf_record))


main(sample_config)
#if __name__ == '__main__':
#    tf.app.run()