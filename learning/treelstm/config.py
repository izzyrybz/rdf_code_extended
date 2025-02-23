import argparse
import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='PyTorch TreeLSTM for Question-Query Similarity on Dependency Trees')
    #
    parser.add_argument('--mode', default='train',
                        help='mode: `train` or `test`')
    parser.add_argument('--data', default='./learning/treelstm/data/lc_quad/',
                        help='path to dataset')
    parser.add_argument('--glove', default='../../data/glove/',
                        help='directory with GLOVE embeddings')
    parser.add_argument('--save', default='learning/treelstm/checkpoints/',
                        help='directory to save checkpoints in')
    parser.add_argument('--load', default='checkpoints/',
                        help='directory to load checkpoints in')
    parser.add_argument('--expname', type=str, default='lc_quad',
                        help='Name to identify experiment')

    # model arguments
    parser.add_argument('--input_dim', default=150, type=int,#used to be 300
                        help='Size of input word vector')
    parser.add_argument('--mem_dim', default=45, type=int, #used to be 150
                        help='Size of TreeLSTM cell state')
    parser.add_argument('--hidden_dim', default=45, type=int, #used to be 50
                        help='Size of classifier MLP')
    parser.add_argument('--num_classes', default=2, type=int,
                        help='Number of classes in dataset')
    # training arguments
    parser.add_argument('--epochs', default=15, type=int,
                        help='number of total epochs to run')
    parser.add_argument('--batchsize', default=15, type=int,
                        help='batchsize for optimizer updates')
    parser.add_argument('--lr', default=0.01, type=float,
                        metavar='LR', help='initial learning rate')
    parser.add_argument('--wd', default=0.00225, type=float,
                        help='weight decay (default: 1e-4)')
    parser.add_argument('--sparse', action='store_true',
                        help='Enable sparsity for embeddings, \
                              incompatible with weight decay')
    parser.add_argument('--optim', default='adagrad',
                        help='optimizer (default: adagrad)')
    parser.add_argument('--sim', default='nn',
                        help='similarity (default: nn) nn or cos')
    # miscellaneous options
    parser.add_argument('--seed', default=123, type=int,
                        help='random seed (default: 123)')
    cuda_parser = parser.add_mutually_exclusive_group(required=False)
    cuda_parser.add_argument('--cuda', dest='cuda', action='store_true')
    cuda_parser.add_argument('--no-cuda', dest='cuda', action='store_false')
    parser.set_defaults(cuda=True)

    args = parser.parse_args()
    return args
