import os
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

import utils
from dataset import Dataset
from engine import train_one_epoch
import transforms as T


def get_model():
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 5)  # 5 is the number of classes
    return model


def get_transform(train):
    transforms = []
    transforms.append(T.ToTensor())
    if train:
        transforms.append(T.RandomHorizontalFlip(0.5))
    return T.Compose(transforms)


def main():

    # load dataset
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # path to object-detection folder
    dataset_path = os.path.join(root_path, "data_collection/dataset")  # path to dataset folder
    dataset = Dataset(dataset_path, get_transform(train=True))

    # define training data loader
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=True,
                                              num_workers=4, collate_fn=utils.collate_fn)

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model = get_model()
    model.to(device)

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)  # construct an optimizer
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)  # and a learning rate scheduler

    # let's train it for 10 epochs
    num_epochs = 10

    for epoch in range(num_epochs):
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        print("trained one epoch")
        # update the learning rate
        lr_scheduler.step()
        print("Saving weights...")
        model_dir_path = os.path.dirname(os.path.realpath(__file__))
        weights_path = os.path.join(model_dir_path, "weights/model.pt")
        torch.save(model.state_dict(), weights_path)

    print("That's it!")


if __name__ == "__main__":
    main()
