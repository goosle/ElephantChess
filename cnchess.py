import pygame as pyg
import os
import sys
import numpy as np

#from Net import Net
from MCTS import MCTS
from Board import Board

main_dir = os.path.split(os.path.abspath(__file__))[0]
SCREENRECT = pyg.Rect(0, 0, 720, 800)
CHESS_TYPE = [1,2,3,4,5,6,7]#King，mandarin,elephant,knight,rook,cannon,pawn

CHESS_WIDTH = 80
CHESS_HEIGHT= 80
BOARD_ROWS = 10
BOARD_COLS = 9
RED_PLAYER_NUM = 1
BLACK_PLAYER_NUM = 2

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'res', file)
    try:
        surface = pyg.image.load(file)
    except pyg.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pyg.get_error()))
    return surface.convert()


class ChessMan :
    '''
    @1 playNum: 1 ='red' ,2='black'
    @2 id : object ID
    @3 pos: object position
    '''
    def __init__(self,world,playerNum,id,pos):
        self.world = world
        self.playerNum = playerNum
        self.id = id
        
        self.chessType = abs(id) // 10
        self.chessNum = abs(id) % 10
        
        self.pos = pos
        self.isDead = False

        self.checked = False

        fn = str(self.playerNum*10+self.chessType)+'.gif'
        self.img = load_image(fn)  



    def draw(self,sufface):  
        row = self.pos // 10
        col = self.pos % 10      
        posx = col*CHESS_WIDTH
        posy = row*CHESS_HEIGHT
        sufface.blit(self.img,(posx,posy))
        if (self.checked):
            pyg.draw.rect(sufface,(255,0,0),[posx,posy,CHESS_WIDTH,CHESS_HEIGHT],3)

    def atPos(self,pos):
        return True if self.pos == pos else  False
    
    def setChecked(self,checked):
        self.checked = checked  
        print(self.id ,' checked set ',checked)

    def move(self,pos):
        self.pos = pos  
 



        

   


class World :
    


    def __init__(self,screen):
         #type+number of count,left->right,bottom->top
        my_obj_init_list = [11,21,22,31,32,41,42,51,52,61,62,71,72,73,74,75]
        op_obj_init_list = [-11,-21,-22,-31,-32,-41,-42,-51,-52,-61,-62,-71,-72,-73,-74,-75]
        my_obj_init_pos  = [94, 93, 95 ,92 ,96 ,91, 97, 90, 98, 71,77,60,62,64,66,68]# row(0,8),col(0,9)
        op_obj_init_pos  = [4, 3, 5 ,2 ,6 ,1, 7, 0, 8, 21,27,30,32,34,36,38]# row(0,8),col(0,9)
        
        self.boardPos =np.array( [
                    [-51, -41, -31, -21, -11, -22, -32, -42, -52],                    
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, -61, 0, 0, 0, 0, 0, -62, 0],
                    [-71, 0, -72, 0, -73, 0, -74, 0, -75],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [71, 0, 72, 0, 73, 0, 74, 0, 75],                    
                    [0, 61, 0, 0, 0, 0, 0, 62, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [51, 41, 31, 21, 11, 22, 32, 42, 52],
                    ])
        

        self.bg = load_image('boardchess.gif')  
        self.screen = screen      
       
        self.currentChecked = None
        self.curTurn = RED_PLAYER_NUM
        self.firstTurn =  RED_PLAYER_NUM # first turn ID > 0
        self.moveItems = []
        self.objs = dict()
        for i,id in enumerate(my_obj_init_list):
            self.objs[id] = ChessMan(self,RED_PLAYER_NUM,id,my_obj_init_pos[i])
        for i,id in enumerate(op_obj_init_list):
            self.objs[id] = ChessMan(self,BLACK_PLAYER_NUM,id,op_obj_init_pos[i])
        

        #self.net = Net('./best_policy_1900.model')  # './best_policy_4.model'
        # 第一个和第二个棋手，  ai 1   人0
        self.board = Board( 1,0)
        #'''如果是双人对战，注释以下五行，并把上面的1,0改为1,1
        #self.mcts = MCTS(self.net, self.board)
        #mcts is fisrt go
        #self.board.next_move = self.mcts.get_move()
        #self.board.move()
        #self.board.change_side()
        #self.mcts.board = self.board
        #self.mcts.update_with_move()

        print('game begin player : %d '%(self.board.current_player_start))
       


    def draw(self,sufface):
        for obj in self.objs.values():
            obj.draw(sufface)
    


    def update(self,screen):
        screen.blit(self.bg,(0,0)) 
        self.draw(screen)
        pyg.display.update()

    
    def exchangeTurn(self):
        self.curTurn =RED_PLAYER_NUM if self.curTurn == BLACK_PLAYER_NUM else BLACK_PLAYER_NUM


    def setValidMoves(self,inputImage,layer,objPos,mvs,rowMin,rowMax,colMin,colMax):
        valids = []
        objPos = objPos + np.array(mvs)
        for pos in objPos:           
            if (pos // 10 )< rowMin or (pos // 10 ) > rowMax:
                continue # row over
            if (pos % 10 )< colMin or (pos % 10 ) > colMax:
                continue # col over
            if(self.boardPos[pos//10][pos%10] > 0) :
                continue
            valids.append(pos)
        for pos in valids :
            inputImage[layer][pos//10][pos%10] = 1
        return valids
     
    def generateInputs(self):
        #input  输入：己方棋子布局，0
        #       我方每个棋子的有效行走图，死棋全为0，共16个平面 1-16
        #       对方棋子布局 17
        #       对方上次移动的位置，18
        #       共19个平面
        inputImage = np.zeros([19,BOARD_ROWS,BOARD_COLS])
        a = np.where(self.boardPos>0,1,0)
        inputImage[0] = a
        rookLine = np.append(np.arange(-90,0,10), np.arange(10,100,10))
        rookLine =np.append(rookLine,np.arange(1,9))
        rookLine= np.append(rookLine,np.arange(-8,0))

        for _,obj in self.objs.items() :
            objType = obj.chessType 
            objCount = obj.chessNum
            objPos = obj.pos
    
            if objType == 1 : #king
                baseLayer = 1
                if obj.isDead :
                    print("king is dead !!!")
                mvs = [ -1 ,1 ,10,-10] # left move = - ,up move = -
                self.setValidMoves(inputImage,objType,objPos,mvs,7,9,3,5)                        
            elif objType == 2 : #kingman
                mvs = [-10-1,-10+1,10-1,10+1]  
                baseLayer = 2
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,7,9,3,5)               
            elif objType == 3: #elphant
                mvs = [-20-2,-20+2,20-2,20+2]  
                baseLayer = 4
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,0,9,0,8) 
            elif objType == 4 :#knight
                mvs = [-10-2,-10+2,10-2,10+2,-20-1,-20+1,20-1,20+1]  
                baseLayer = 5
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,0,9,0,8)   
            elif objType == 5: #rook
                mvs = rookLine 
                baseLayer = 7
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,0,9,0,8)
            elif objType == 6: #cannon
                mvs = rookLine 
                baseLayer = 9
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,0,9,0,8)
            elif objType == 7: #pawn
                if(objPos//10>5):
                    mvs = [-10,10,-1,1]
                else:
                    mvs = [-10] 
                baseLayer = 11
                if obj.isDead :
                    inputImage[baseLayer+objCount-1] = 0
                else:
                    self.setValidMoves(inputImage,baseLayer+objCount-1,objPos,mvs,0,9,0,8)

        #对方棋子布局，
        a = np.where(self.boardPos<0,1,0)
        inputImage[17] = a

        if self.moveItems== None :
            inputImage[18] = 0
        else :
            _ ,pos = self.moveItems[-1]
            inputImage[19][pos // 10][pos%10] = 1    
        print(inputImage)
        return inputImage


    def getSelect(self,pos):
        checked = None
        row = pos // 10
        col = pos % 10
        id = self.boardPos[row,col]
        if  id > 0:
            checked = self.objs[id]
        return checked

    def moveInBoard(self,srcObj,dstPos):
        sr = srcObj.pos // 10
        sc = srcObj.pos % 10
        dr = dstPos // 10
        dc = dstPos % 10
        self.boardPos[sr][sc] = 0
        self.boardPos[dr][dc] = srcObj.id
        

    def move(self,srcObj,dstPos):
        self.moveInBoard(srcObj,dstPos)
        srcObj.mov(dstPos)
        self.moveItems.append([srcObj.id,dstPos]) 
        
    def checked(self,pos):
        selObj = self.getSelect(pos)
        if  self.currentChecked and self.currentChecked != selObj:
            if None != selObj :
                if( self.currentChecked.playerNum == selObj.playerNum):
                    #exchagne select
                    self.currentChecked.setChecked(False)
                    self.currentChecked = None
                    selObj.setChecked(True)
                    self.currentChecked = selObj
                elif self.canMove(self.currentChecked.pos,selObj.pos):
                    self.killObj(self.currentChecked,selObj) #kill sel 
                    self.move(self.currentChecked,pos)
                    self.currentChecked.setChecked(False)
                    self.currentChecked = None
                    self.exchangeTurn()   
                    self.aiMove()
            else:      
                #move slect    
                if self.canMove(self.currentChecked.pos,pos):
                    self.move(self.currentChecked,pos)
                    self.currentChecked.setChecked(False)
                    self.currentChecked = None
                    self.exchangeTurn() 
                    self.aiMove()

        elif None != selObj and self.currentChecked != selObj:
                #set select
                if (selObj.playerNum == self.curTurn):
                    selObj.setChecked(True)
                    self.currentChecked  = selObj  
    


    def canMove(self,srcPos,dstPos):       
        aiPos = srcPos*100 +dstPos  
        self.board.next_move = aiPos 
        self.board.find_move()
        print(" from ", srcPos,' to ' ,dstPos)
        if self.board.next_move not in self.board.valid_move:
            print("can't move from ", srcPos ,' to ' ,dstPos)
            return False   
        self.board.move()     
            
        return True

    

    def aiMove(self):
        self.board.not_end()
        if not self.board.not_end_number:
            print("game over ,winner is %d"%(self.board.winner))
            return         
        
        net_input = self.board.decode_board()
        action_probs, _ =[],0# self.net.policy_value([net_input])
        #self.board.next_move = self.board.get_best_move(action_probs[0]) #fetch from best probility of net
        self.board.next_move = 0#self.mcts.get_move()  # 格式 xyab
        
        self.board.move()
        
        move = self.board.next_move
        start = move//100
        end = move%100
        selsrc = self.getSelect(start)
        if(None == selsrc):
            print( ' error ai src' ,start)
        seldst = self.getSelect(end)
        if None != seldst :     
            #ai kill 
            self.killObj(selsrc,seldst)
        # ai move
        selsrc.move(end)
        #selsrc.setChecked(True)
        #self.currentChecked = selsrc
        
        self.exchangeTurn() 

    def killObj(self,src,dst):
        #to do : check can move
        print('destst ' , dst.id ,' was killed by ' ,src.id)
        if(dst.playerNum == src.playerNum):
            return False
        dst.isDead = True    
        self.objs.pop(dst.id)
        return True

    def start(self):
        print('start game!')
        tclock = pyg.time.Clock()
        needExit = False
        while not needExit:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    needExit = True
                elif event.type == pyg.MOUSEBUTTONDOWN:
                    mouseTypes = pyg.mouse.get_pressed()
                    if mouseTypes[0] :
                        mx, my = pyg.mouse.get_pos()
                        row = my//CHESS_HEIGHT
                        col = mx//CHESS_WIDTH                        
                        self.checked(row*10+col)
                        
                        
            tclock.tick(20)
            self.update(self.screen)
def main():
    pyg.init()
    testmode = pyg.display.mode_ok(SCREENRECT.size, 0, 32)
    screen = pyg.display.set_mode(SCREENRECT.size,0,32)
    pyg.display.set_caption("hello")
     
    world = World(screen)
    #world.start() 
    i = world.generateInputs()
    print(i)

if __name__ == '__main__':
    main()
