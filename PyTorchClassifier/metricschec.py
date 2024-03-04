import torch
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import torch.utils
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet
net = resnet.ResNet(resnet.Bottleneck, [2,2,2,2])

if __name__=="__main__":
    PATH = './good_model_resnet.pth'
    net.load_state_dict(torch.load(PATH))
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    batch_size = 4
    dataset = torchvision.datasets.ImageFolder("actualdataset/", transform=transform)

    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=2)

    classes = ("match", "dontcareaboutthat")
    # prepare to count predictions for each class
    correct_pred = {classname: 0 for classname in classes}
    total_pred = {classname: 0 for classname in classes}

    # again no gradients needed
    with torch.no_grad():
        for data in dataloader:
            images, labels = data[0].to("cuda"), data[1].to("cuda")
            outputs = net(images)
            _, predictions = torch.max(outputs, 1)
            # collect the correct predictions for each class
            for label, prediction in zip(labels, predictions):
                if label == prediction:
                    correct_pred[classes[label]] += 1
                total_pred[classes[label]] += 1

    # print accuracy for each class
    for classname, correct_count in correct_pred.items():
        accuracy = 100 * float(correct_count) / total_pred[classname]
        print(f'Accuracy for class: {classname:5s} is {accuracy:.1f} %')