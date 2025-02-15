
from utils import load_dataset, booleanize_positions_3d, \
    display_board, get_board_at_n_moves_before_the_end, create_n_moves_before_the_end_dataset, \
        save_dataset
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
    
def create3d_board_representation(board):
    """
    Used to create a 3d voxel plot of a booleanized board.
    
    In one of the early prototypes we tried to use 2 layer convolution, 
    and output from this method was used in the presentation.
    
    This method was made by modifying 
    https://matplotlib.org/stable/gallery/mplot3d/voxels_numpy_logo.html#sphx-glr-gallery-mplot3d-voxels-numpy-logo-py
    """
    board = booleanize_positions_3d(board)
    def explode(data):
        size = np.array(data.shape)*2
        data_e = np.zeros(size - 1, dtype=data.dtype)
        data_e[::2, ::2, ::2] = data
        return data_e

    # build up the numpy logo
    n_voxels = np.zeros((2, 7, 7), dtype=bool)
    for z in range(board.shape[0]):
        for y in range(board.shape[1]):
            for x in range(board.shape[2]):
                n_voxels[z, y, x] = board[z, y, x] == 1
    facecolors = np.where(n_voxels, '#FFFFFFFF', '#000000FF')
    edgecolors = np.where(n_voxels, '#BFAB6E', '#7D84A6')
    filled = np.ones(n_voxels.shape)

    # upscale the above voxel image, leaving gaps
    filled_2 = explode(filled)
    fcolors_2 = explode(facecolors)
    ecolors_2 = explode(edgecolors)

    # Shrink the gaps
    x, y, z = np.indices(np.array(filled_2.shape) + 1).astype(float) // 2
    x[0::2, :, :] += 0.05
    y[:, 0::2, :] += 0.05
    z[:, :, 0::2] += 0.05
    x[1::2, :, :] += 0.95
    y[:, 1::2, :] += 0.95
    z[:, :, 1::2] += 0.95

    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(x, y, z, filled_2, facecolors=fcolors_2, edgecolors=ecolors_2)
    ax.set_aspect('equal')

    plt.show()

def create_table_of_boardv2(board):
    new_board = np.zeros((board.shape[0], board.shape[1] * 2), dtype=int)
    for y in range(board.shape[0]):
        for x in range(board.shape[1]):
            if board[y, x] == 1:
                new_board[y, x] = 1
            
            elif board[y,x] == -1:
                new_board[y, x + board.shape[1]] = 1
    
    for y in range(new_board.shape[0]):
        print("&".join(new_board[y].astype(str)))

def get_unique_games():
    games = set()
    with open("9x9_games.txt") as file:
        for line in file.readlines():
            games.add(line)
    
    return games

def create_dataset_from_captured_dataset():
    # Get boards and winner at n moves before the end
    bs, ws = create_n_moves_before_the_end_dataset(Path(__file__).parent / "captured" / "combined_red.txt", 9, 5, -1)

    # Filter out boards that are equal:
    boards = []
    winners = []
    
    bset = set()
    for (b,w) in zip(bs, ws):
        
        # Prevent duplicate boards in the dataset
        boardstring = ",".join(b.flatten().astype(str))
        if boardstring in bset:
            continue
        
        bset.add(boardstring)
        boards.append(b)
        winners.append(w)
    
    # Save to csv file
    save_dataset(boards, winners, Path(__file__).parent / "dataset"/ "hex_9x9_5moves.csv")

    # Test that it loads and print size of dataset
    boards, winners = load_dataset("hex_9x9_5moves.csv")

    print("Num unique games:", len(boards))
    
def create_dataset_splits():
    X, Y = load_dataset("hex_games_1_000_000_size_7.csv", num_rows=100_000)
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, stratify=Y, test_size=0.2)
    
    save_dataset(X_train, Y_train, Path(__file__).parent / "dataset"/ "hex_games_1_000_000_size_7_train.csv")
    save_dataset(X_test, Y_test, Path(__file__).parent / "dataset"/ "hex_games_1_000_000_size_7_test.csv")
    
    
def create_img_for_2_moves_before_end():
    file = open(Path(__file__).parent / "captured" / "combined_red.txt")
    line = file.readline()
    data = line.strip().split(",")
    data = [int(i) for i in data]
    winner = data[-1]
    history = data[:-1]
    board = get_board_at_n_moves_before_the_end(9, history, 0, -1)
    display_board(board)

    board = get_board_at_n_moves_before_the_end(9, history, 2, -1)
    display_board(board)
    
    board = get_board_at_n_moves_before_the_end(9, history, 5, -1)
    display_board(board)
    

def create_n_moves_before_the_end_param_search_plot():
    csv = pd.read_csv(Path(__file__).parent / "report-performance-analysis" / "2 moves before the end" / "2_before_performance_20241208_152741.csv")
    
    s_values = [5, 10, 15, 20, 25, 30]

    for s in s_values:
        rows = csv[csv["s"] == s]
        plt.plot(rows["number of clauses"], rows["max accuracy"], label = f"S={s}")


    plt.xlabel("Number of clauses")
    plt.ylabel("Accuracy")

    plt.legend()
    plt.show()
    
def create_number_of_clauses_completed_games_plot():
    csv = pd.read_csv(Path(__file__).parent / "report-performance-analysis" / "completed games" / "number_of_clauses_accuracy_20241207_095217.csv")

    num_clauses = csv["number of clauses"]
    acc = csv["max accuracy"]

    plt.plot(num_clauses, acc)
    plt.xlabel("Number of clauses")
    plt.ylabel("Accuracy")

    plt.show()


#boards, winners = load_dataset("hex_games_1_000_000_size_7.csv", num_rows = 10)
#
#display_as_graph(positions[1])
#create3d_board_representation(positions[1])
#position = positions[1]
#winner = winners[1]
#
#print(position)
#print(winner)

#display_position(position)
#
#print(booleanize_positions_v2(positions[1:2]))
#

#create_table_of_boardv2(boards[1])
#display_position(board3)
#create_img_for_2_moves_before_end()
#create_dataset_from_captured_dataset()
#csv = pd.read_csv("train_20241127_104205.csv")
#
#create_accuracy_plot("accuracy.png", csv["train accuracy"], csv["test accuracy"])
#create_dataset_splits()
#create_n_moves_before_the_end_param_search_plot()

board = np.array([
    [0, 0, 0, 0, -1, 0, 0],
    [0, 0, 0, 0, -1, 0, 0],
    [0, 1, 1, 1, -1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 0, 1, 1],
    [0, 0, 0, -1, 0, 0, 0],
    [0, 0, -1, 0, 0, 0, 0]
])


#Clause 4860 (length 14): B_5_5 AND 
# CB_1_4_6_8 AND CB_4_4_5_5 AND CB_1_0_6_0
# CR_2_0_6_5 AND CR_1_5_3_7 AND CR_1_1_5_4

# NOT CR_4_0_1_4 AND NOT CR_3_2_8_3 AND NOT CR_4_4_6_8
# AND NOT CB_3_1_7_3 AND NOT CB_1_2_7_8 AND NOT CB_7_4_0_6 AND NOT CB_0_6_7_7
board_9x9 = np.array([
    [0, 1, -1, 0, 0, 0, 1, 0, 0],
    [0, -1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, -1, 0, 0, 0],
    [0, -1, 0, 0, 0, 1, -1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0],
])

display_board(board_9x9, show_coordinates=True)