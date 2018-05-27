#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: prunetruong

to launch:
python openV4_create_database.py --path_openV4_annotation '/Volumes/PRUNE/Visually-Impaired-Transport-Assistance/openV4/annotations' 
--path_openV4_images '/Volumes/PRUNE/Visually-Impaired-Transport-Assistance/mixed/images/'
--step_val_train_test train
--path_text_file '/Users/prunetruong/Desktop/Blind_project/Visually-Impaired-Transport-Assistance/data/openV4/category_classes_openV4.txt'

"""

import csv
import os
import urllib.request
from PIL import Image
import argparse
import sys
import warnings
import shutil        
import base64

def make_json_file(text, categories_path):
    '''from the Text file containing the informations on the categories we want to 
    download in the database, creates a list information + a vector classes_to_download
    input: path to the text_file
    Also, for the label name given, finds the corresponding id in categories_path'''
    
    print('checking for existence of category...')
    categories=[]
    classes_to_download=[]
 
    for x in open('{}'.format(text)).readlines():
        row=x.split(",")
        label_exist=0
        with open(categories_path, 'r') as file: 
            for line in csv.reader(file):
                if (line[1].lower()==row[0]):
                    category={'label_number': line[0], 'label': row[0], 'label_id': row[1]}
                    categories.append(category)
                    classes_to_download.append(line[0])
                    label_exist=1
                    print('category {} exists'.format(row[0]))
                    continue
            if label_exist==0: 
                sys.exit('warning: {} is not a valid category name. Please change it. Stop execution'.format(row[0]))
                
            
    return(categories, classes_to_download)

def format_annotations(annotation_path, trainable_classes, categories):
    '''trainable_classes_path contains a list of the category we are interested in, 
    annotation_path contains all the annotations for bounding box for all images. 
    
    output:  annotation_bbx: a list containing the bounding box informations of the
    images of the categories in "trainable_classes".
    ids: the list of the corresponding image ids
    
    ex: ids= ['ibeineodn', 'bcienocnen']
    annotations_bbx[{'id': row[0], 'label': row[2], 'confidence': row[3], 'x0': row[4],
                          'x1': row[5], 'y0': row[6], 'y1': row[7]}]
    '''
    
    annotations_bbx = []
    ids = []
  
    with open(annotation_path, 'r') as annofile:
        for row in csv.reader(annofile):
            label_number_dataset=row[2]
            if label_number_dataset in trainable_classes:
                
                for line in categories: 
                    #line each time contains {{'label_number': line[0], 'label': row[0], 'label_id': row[1]}}
                    #we get the information on the category
                    if line['label_number']==label_number_dataset:
                        label=line['label']
                        label_id=line['label_id']
                        
                annotation = {'id': row[0], 'label_number': row[2],'label':label, 'label_id':label_id,
                              'confidence': row[3], 'xmin': row[4],'xmax': row[5], 'ymin': row[6], 'ymax': row[7]}
                annotations_bbx.append(annotation)
                if not row[0] in ids:
                    #here we exclude the name of images that appear several times (the ones that have several annotations)
                    ids.append(row[0])

    print('there are {} images of {} available in openV4 dataset'.format(len(ids), ' '.join(trainable_classes)))
    print('there are {} corresponding annotations'.format(len(annotations_bbx)))

    return annotations_bbx, ids

def list_image_to_download(path_to_download, ids):
    '''check if there are already images from the ids list that are downloaded. 
    Otherwise, lists the image_id that need to be downloaded'''
    
    #l=0
    image_to_download=[]
    for name in ids:
        #if os.path.exists('{}/{}.jpg'.format(path_to_download, name)):
            #with open('{}/{}.jpg'.format(path_to_download, name), "rb") as image_file:
                #encoded_string = base64.b64encode(image_file.read())
                #if not encoded_string.endswith(b'/9k='):
                    #l+=1
                    #print(name)
                    #shutil.move('{}/{}.jpg'.format(path_to_download, name), '/Users/prunetruong/Desktop/corrupted_file/')
        if not os.path.exists('{}/{}.jpg'.format(path_to_download, name)):
            image_to_download.append(name)
    #print(l)
    return image_to_download

def format_image_index(images_path, ids):
    '''finds the corresponding url for a list of ids images
    input: images_path is the annotation file of all the images in the database
    ids is the list of image_ids of which we want to retrieve url
    output: images is a list containing image_id, url '''
    
    
    images = []
    with open(images_path, 'r') as f:
        print('getting url for images /n this may take a while... ')
        
        reader = csv.reader(f)
        dataset = list(reader)
        print('we went through the list of images in the database, now finding the url')
        i=0
        l=0
        for row in dataset:
            image = {'id': row[0], 'url': row[2]}
            if image['id'] in ids:
                images.append(image)
                print(image['url'])
                i+=1
                if (i%1000==0):
                    print('found {} images'.format(i))
                if not image['url'].endswith('.jpg'): 
                    l+=1
                    print(image['url'])
                
    print('there are {} images that do not end with .jpg that we need to download'.format(l))
    print('we have {} images to download'.format(len(images)))
    
    return images

def download_images(path_to_download, list_images, number): 
    '''download images from a url list'''
    
    print('start downloading {}'.format(number))
    i=0
    for name in list_images:
        file_name=name['id']
        try: 
            urllib.request.urlretrieve(name['url'],
                                       '{}/{}.jpg'.format(path_to_download,file_name)) 
            i+=1
            print('downloaded {}.jpg, {}/{}'.format(file_name, i, number))
        except:
            print('error downloading {}.jpg: skipping'.format(file_name))
    print('end of download')

def downsampling_images(path_source_images, path_destination_images, desired_width):
    print('we are downsampling the images present in {}'.format('path_source_images'))
    i=0
    width = desired_width
    for file in os.listdir('{}'.format(path_source_images)):
        if file.endswith('.jpg'):
            if not os.path.exists('{}/{}'.format(path_destination_images, file)):
                img = Image.open('{}/{}.jpg'.format( path_source_images, file.strip('.jpg') ))
                width_rel= (width/float(img.size[0]))
                height = int((float(img.size[1])*float(width_rel)))
                try: 
                    img = img.resize((width, height), Image.ANTIALIAS) 
                    img.save('{}/{}'.format(path_destination_images,file))
                    i+=1
                    os.remove('{}/{}.jpg'.format(path_source_images, file))
                except: 
                    print('could not downsampled image {}'.format(file))
    print('downsampled {} images'.format(i))
        
def create_csv(name_csv, directory_annotation, directory_image, annotations_bbx, step):
    warnings.filterwarnings('error')
    todelete=[]
    i=0
    if os.path.exists('{}/{}.csv'.format(directory_annotation, name_csv)):
        os.remove('{}/{}.csv'.format(directory_annotation, name_csv))
    print('creating a csv file ...')
    with open('{}/{}.csv'.format(directory_annotation, name_csv), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvfile.write('img_name;category;category_idx;height;width;x_min;y_min;x_max;y_max\n')
        for image in annotations_bbx: 
            image_id=image['id']
            if os.path.exists('{}/{}.jpg'.format(directory_image, image_id)):
                try: 
                    
                    Image_to_describe = Image.open('{}/{}.jpg'.format(directory_image, image_id))
                    width, height = Image_to_describe.size
                    i+=1
                #print('{} image has a size of {} height and {} width'.format(image_id, width, height))
                    writer.writerow([image_id, image['label'], image['label_id'], height, width, image['xmin'],image['ymin'],image['xmax'],
                             image['ymax']])
                except Warning: 
                    print('image not written in csv')
                    todelete.append(image_id)
        print('csv file created in {} with {} annotations'.format(directory_annotation, i))
    for name in todelete:
        os.remove('{}/{}.jpg'.format(directory_image, name))
        print('{} deleted'.format(name))


parser = argparse.ArgumentParser()
parser.add_argument('--path_openV4_annotation', dest='path_annotation', required=True)
parser.add_argument('--path_openV4_images', dest='path_images', required=True)
parser.add_argument('--step_val_train_test', dest='step', required=True)
parser.add_argument('--path_text_file', dest='fichier_text', required=True)

if __name__ == '__main__':

    args = parser.parse_args()
    path_annotation= args.path_annotation
    path_images=args.path_images
    step = args.step
    fichier_text = args.fichier_text
    
    bbox_annotation_path='{}/bbox_annotations/{}/annotations-human-bbox.csv'.format(path_annotation, step)
    images_annotation_path='{}/images/{}/images.csv'.format(path_annotation,step)
    classes_description_path='{}/classes/class-descriptions.csv'.format(path_annotation)

    path_intermediary='{}/dataset_{}_big_images'.format(path_images, step)
    path_to_download='{}/dataset_{}_down_sampled'.format(path_images,step)
    
    categories_information, list_classes=make_json_file(fichier_text, classes_description_path)
    annotations, list_image_ids = format_annotations(bbox_annotation_path, list_classes, categories_information)
    desired_width = 600
    create_csv('label_{}'.format(step), path_annotation, path_to_download, annotations, step)
    #if we want to download images, remove create_csv above and remove ''' below
    
'''
    list_image_id_to_download=list_image_to_download(path_to_download, list_image_ids)
    if list_image_id_to_download:
        if not os.path.exists('{}'.format(path_intermediary)):
            os.makedirs('{}'.format(path_intermediary))
        list_images_url=format_image_index(images_annotation_path, list_image_id_to_download)
        download_images(path_intermediary, list_images_url, len(list_images_url))
        downsampling_images(path_intermediary, path_to_download, desired_width)
    create_csv('label_{}'.format(step), path_annotation, path_to_download, annotations, step)
'''
    


