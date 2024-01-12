from tkinter import font as tkFont
import tkinter as tk
from sudoku import SudokuGrid, generateFullSample


cellSize = 52;
outPad = 12;
inPad = 1;
betPad = 4;
lineSize = 5;

def generateSubGrid(parent, cellSize, pad, photo, x=3, y=3):
    frame = tk.Frame(parent);
    start = 1;
    for i in range(y):
        for j in range(x):
            btn = tk.Button(frame,text=start,image=photo,compound="c",width=cellSize,height=cellSize);
            btn.grid(row=i,column=j,padx=pad,pady=pad);
            btn.image = photo;
            btn.config(font=("Helvetica", 28, "bold"));
            start += 1;
    return frame;

def colorCells(sudokuGrid, cells, color):
    # set marks
    for c in cells:
        sudokuGrid.getElement(c[1], c[0]).config(fg=color);
    #return sudokuGrid;

# sudokuGrid = [9][9], (tkinter element, int value)
def openSample(grid, title = "Sample", color = "black"):
    global win
    win = tk.Tk();
    win.geometry("600x600");
    win.title(title);
    #sudokuFont = tkFont.Font(family='Helvetica', size=28, weight='bold');
    sudokuGrid = SudokuGrid();
    # main grid frame
    global mainFrm
    mainFrm = tk.Frame(win);
    mainFrm.pack();
    # canvas
    global mainCnv
    mainCnv = tk.Canvas(mainFrm);
    mainCnv.pack();
    overGrid = [];
    global photo;
    photo = tk.PhotoImage(width=1,height=1, master=win);
    #pics = [];  # stop image from becoming garbage
    for i in range(3):
        for j in range(3):
            newFrm = generateSubGrid(mainCnv, cellSize, inPad, photo);
            overGrid.append(newFrm);
            overGrid[3*i + j].grid(row=i,column=j,
                                   padx=((outPad if (j == 0) else betPad), outPad if (j == 2) else betPad),
                                   pady=((outPad if (i == 0) else betPad), outPad if (i == 2) else betPad));
            newFrm.update();
            # get all buttons in subgrid
            y = i * 3;
            x = j * 3;
            children = newFrm.winfo_children();
            #print("----");
            for item in children:
                # set value
                val = grid[y][x];
                item.configure(text=str(val));
                if (val == None or val == 0):
                    item.configure(text="");
                sudokuGrid.grid[9*y + x] = list((item, val));
                sudokuGrid.getElement(x, y).config(fg=color);
                # next iteration
                x += 1;
                if ((x % 3) == 0):
                    y += 1;
                    x = j * 3;
    # set invalid marks
    #if (invalid != None):
    #    for c in invalid:
    #        sudokuGrid.getElement(c[1], c[0]).config(fg="red");
    # set known marks
    #if (known != None):
    #    for c in known:
    #        sudokuGrid.getElement(c[1], c[0]).config(fg="gray");
    mainFrm.update();
    ## draw grid on canvas
    winw = mainFrm.winfo_width() ;
    winh = mainFrm.winfo_height();
    outp = outPad // 2;
    #  outline
    mainCnv.create_line(outp, outp, outp, winh - outp, fill="green", width=lineSize);                           # left
    mainCnv.create_line(winw - outp, outp, winw - outp, winh - outp / 2, fill="green", width=lineSize);         # right
    mainCnv.create_line(outp / 1.5, 6, winw - (outp / 2), 6, fill="green", width=lineSize);                     # top
    mainCnv.create_line(outp / 1.5, winw - outp, winw - outp / 2, winw - outp, fill="green", width=lineSize);   # bottom
    #  separators
    winw = winw - outp / 2;
    winh = winh - outp / 2;
    cs = cellSize + 7;
    delta0 = outPad + (cs + inPad * 2) * 3 + betPad * 1.5;
    delta1 = delta0 + betPad + (cs + inPad * 2) * 3 + betPad * 1.75;
    mainCnv.create_line(delta0, outp, delta0, winh, fill="green", width=lineSize);          # vert 1st
    mainCnv.create_line(delta1, outp, delta1, winh, fill="green", width=lineSize);          # vert 2nd
    mainCnv.create_line(outp, delta0, winw, delta0, fill="green", width=lineSize);          # hor 1st
    mainCnv.create_line(outp, delta1, winw, delta1, fill="green", width=lineSize);          # hor 2nd
    mainCnv.update();
    return (sudokuGrid, photo);


if __name__ == "__main__":
    (inputGrid, solGrid, removedCells) = generateFullSample(44);
    openSample(solGrid);
