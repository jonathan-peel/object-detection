import os
import numpy as np
import torch
from PIL import Image, ImageShow


class Dataset(torch.utils.data.Dataset):

    def __init__(self, root, transforms):
        self.root = root  # path to dataset folder
        self.transforms = transforms

        # Count dataset size
        self.dataset_size = 0
        fileidx = 0
        filename = f'{fileidx}.npz'
        while os.path.isfile(os.path.join(self.root, filename)):
            self.dataset_size += 1
            fileidx += 1
            filename = f'{fileidx}.npz'

        print(f'[Dataset]: Found dataset with {self.dataset_size} files.')

    def __getitem__(self, idx):
        # access items like this: dataset[index]
        # returns image, target as specified

        filename = f'{idx}.npz'
        path = os.path.join(self.root, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f'[Dataset]: File at {path} does not exist!')

        npzfile = np.load(path)

        img = Image.fromarray(npzfile['arr_0'])
        img = img.convert("RGB")

        boxes = npzfile['arr_1']
        classes = npzfile['arr_2']

        # convert lists to tensors:
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(classes, dtype=torch.int64)
        image_id = torch.as_tensor(idx, dtype=torch.int64)

        target = {
            "boxes": boxes,
            "labels": labels,
            "image_id": image_id
        }

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return self.dataset_size
