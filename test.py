import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from train import autoencoder


def compute_auc(model, test_images, test_labels):
    # Computing reconstruction loss
    y_pred = model.predict(np.concatenate((test_images, test_images), axis=-1))
    diff = y_pred - test_images
    diff = np.sum(diff ** 2, axis=1)

    # Computing AUC
    fpr, tpr, thresholds = roc_curve(test_labels, diff, 1)
    AUC = auc(fpr, tpr)
    print('AUC: ' + str(AUC))

    # Plotting ROC
    plt.plot(fpr, tpr)
    plt.xlabel('TPR')
    plt.ylabel('FPR')
    plt.title('ROC')
    plt.show()


def get_f1(threshold, diff, labels):
    pred = [int(d > threshold) for d in diff]
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for i in range(len(pred)):
        if labels[i] == pred[i] == 1:
            true_positive += 1
        if pred[i] == 1 and labels[i] != pred[i]:
            false_positive += 1
        if labels[i] == pred[i] == 0:
            true_negative += 1
        if pred[i] == 0 and labels[i] != pred[i]:
            false_negative += 1

    if true_positive + false_positive == 0 or true_positive + false_negative == 0:
        return 0
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    if precision + recall == 0:
        return 0
    return 2 * precision * recall / (precision + recall)


def find_f1(model, test_images, test_labels, validation, *args):
    if validation:
        # Finding the best threshold using validation set
        y_pred = model.predict(np.concatenate((args[0], args[0]), axis=-1))
        diff = y_pred - args[0]
        diff = np.sum(diff ** 2, axis=1)

        tmin = min(diff) - 1
        tmax = max(diff) + 1
        f1 = 0
        best_threshold = 0
        for threshold in np.arange(tmin, tmax, 0.1):
            score = get_f1(threshold, diff, args[1])
            if score > f1:
                f1 = score
                best_threshold = threshold

        # Computing reconstruction loss
        y_pred = model.predict(np.concatenate((test_images, test_images), axis=-1))
        diff = y_pred - test_images
        diff = np.sum(diff ** 2, axis=1)

        # Compuring F1 score
        f1 = get_f1(best_threshold, diff, test_labels)
        print('F1: ' + str(f1))
    else:
        # Computing reconstruction loss
        y_pred = model.predict(np.concatenate((test_images, test_images), axis=-1))
        diff = y_pred - test_images
        diff = np.sum(diff ** 2, axis=1)

        # Computing F1 score
        tmin = min(diff) - 1
        tmax = max(diff) + 1
        f1 = 0
        for threshold in np.arange(tmin, tmax, 0.1):
            score = get_f1(threshold, diff, test_labels)
            if score > f1:
                f1 = score
        print('F1: ' + str(f1))


if __name__ == '__main__':
    args = sys.argv
    model_directory = 'model/'
    data_directoy = 'data/'
    if len(args) > 1:
        model_directory = args[1]
        data_directoy = args[1]

    # Loading the data
    meta = np.load(data_directoy + 'meta.npy')
    dataset = meta[0]
    test_images = np.load(data_directoy + 'test_images.npy')
    test_labels = np.load(data_directoy + 'test_labels.npy')

    # Loading the model
    model = autoencoder(test_images.shape[1], 0.1)
    model.load_weights(model_directory + 'weights.hdf5')

    # Computing AUC and F1 score
    if dataset == 'fashion_mnist' or dataset == 'mnist':
        protocol = meta[1]
        if protocol == 'p1':
            validation_images = np.load(data_directoy + 'validation_images.npy')
            validation_labels = np.load(data_directoy + 'validation_labels.npy')
            find_f1(model, test_images, test_labels, True, validation_images, validation_labels)
            compute_auc(model, test_images, test_labels)
        elif protocol == 'p2':
            compute_auc(model, test_images, test_labels)
    elif dataset == 'coil100':
        find_f1(model, test_images, test_labels, False, False, )
        compute_auc(model, test_images, test_labels)
