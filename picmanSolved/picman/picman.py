import pygame
import time
import random
import copy
pygame.init()

#Defining class that will act as entitites in the game

class map:
    def __init__(self,maze):
        self.maze = maze
        self.numberOfCoins = 0 
        self.PlayerTilePos = []
        self.gNodePos = []
        self.gNodes = []
        self.teleportPos = []
        self.homeTiles = []
        self.playerNode = None
        self.ghostHomeNode = None
        self.ghostEaten = False
        self.recentGhostDeath = None
        self.scoreCords = ()
        self.LifeCords = ()
        self.LifeImageCords = ()
        self.playerImage = pygame.image.load("Files\Sprites\PlayerSprites\PR.png")
        self.LevelNo = 1
        self.noCoinsAtStart = 0
        self.nextLevel = True
    
    def getCoins(self,coins):
        y = 0
        for row in self.maze:
            x = 0
            for tile in row:
                if tile == '01' or tile == '03':
                    
                    c = coin("Files/Sprites/Map/nCoin.png",6,6,(110 + x*13),(182 + y*13),'n',x,y)
                    g = Node(c)
                    coins.addNode(coins.first,g)
                    self.numberOfCoins += 1
                    self.noCoinsAtStart += 1
                elif tile == '02' or tile == '04':
                    s = coin("Files/Sprites/Map/sCoin.png",12,12,(110 + x*13),(182 + y*13),'s',x,y)
                    g = Node(s)
                    coins.addNode(coins.first,g)
                    self.numberOfCoins += 1
                    self.noCoinsAtStart += 1
                x += 1
            y += 1

    def getSpawns(self,player,ghosts):
        y = 0
        self.scoreCords = (13 + 110,169 + 13)
        for row in self.maze:
            x = 0
            for tile in row:
                if tile == '15':
                    xPos = (110 + x*13)
                    yPos = (182 + y*13)
                    player.setSpawn(xPos,yPos)
                    player.setxTile(x)
                    player.setyTile(y)
                ####################################################
                elif tile == '13':
                    xPos = (110 + x*13)
                    yPos = (182 + y*13)
                    ghosts.setSpawns(xPos,yPos,x,y)

                    
                elif tile == '00' or tile == '01' or tile == '02': #error when only looking for '00' should be looking through coins as well
                    self.PlayerTilePos.append([pygame.Rect((x*13 + 110),(y*13 + 182),12,12),x,y])
                elif tile == '03' or tile == '04' or tile == '05':
                    self.gNodePos.append([pygame.Rect((x*13 + 110),(y*13 + 182),13,13),x,y])
                elif tile == '17':
                    self.gNodePos.append([pygame.Rect((x*13 + 110),(y*13 + 182),13,13),x,y])
                    self.teleportPos.append([pygame.Rect((x*13 + 110),(y*13 + 182),13,13),x,y])
                elif tile == '19':
                    self.homeTiles.append(pygame.Rect((x*13 + 110),(y*13 + 182),13,13))
                x +=1
            y += 1
        
        self.LifeCords = ((110 + 39),((y+1)*13 + 192))
        self.LifeImageCords = ((110 + 13),((y+1)*13 + 182))    
        return
    
    def rendermap(self,gameDisplay):
        y = 0
        topLeft = pygame.image.load("Files/Sprites/Map/TL.png")
        bottomLeft = pygame.image.load("Files/Sprites/Map/BL.png")
        topRight = pygame.image.load("Files/Sprites/Map/TR.png")
        bottomRight = pygame.image.load("Files/Sprites/Map/BR.png")
        verticalWall = pygame.image.load("Files/Sprites/Map/VW.png")
        horizontalWall = pygame.image.load("Files/Sprites/Map/HW.png")
        for row in self.maze:
            x = 0
            for tile in row:
                if tile == '06':
                    gameDisplay.blit(topLeft,(110 + x*13,182 +y*13))
        
                elif tile == '07':
                    gameDisplay.blit(bottomLeft,(110 + x*13,182 + y*13))
                elif tile == '08':
                    gameDisplay.blit(topRight,(110 + x*13,182 + y*13))
                elif tile == '09':
                    gameDisplay.blit(bottomRight,(110 + x*13,182 +y*13))
                elif tile == '10':
                    gameDisplay.blit(horizontalWall,(110 + x*13,182 +y*13))
                elif tile == '11':
                    gameDisplay.blit(verticalWall,(110+x*13,182+y*13))
                x +=1
       
            y +=1
        return


    
    def getGNodes(self,arry,coins):
        self.gNodes = []
        y = 0
        for row in arry:
            x = 0
            for tile in row:
                if tile == '03' or tile == '04' or tile == '05' or tile == '17':
                    node = gNode((x,y),True,False)
                    node.calculateCost(coins)
                    self.gNodes.append(node)
                elif tile == '20':
                    node = gNode((x,y),True,True)
                    self.gNodes.append(node)
                    self.playerNode = node
                elif tile == '13':
                    node = gNode((x,y),False,False)
                    self.gNodes.append(node)
                    self.ghostHomeNode = node
                x +=1
            y +=1
        return

    def getNodeMapAll(self,player,ghosts,coins):
        arry = copy.deepcopy(self.maze) #Need to make a deep copy because when showing nodes the players node created more and more nodes
        x = player.xTile
        y = player.yTile
        arry[y][x] = '20'
        self.getGNodes(arry,coins)
        transposedArry = [*zip(*arry)]
        self.getNodeMapX(arry)
        self.getNodeMapY(transposedArry)
        self.getPlayerPossibleMoves(player,arry,transposedArry)
        ghosts.checkDistanceFromNodes(arry,transposedArry,self)
        return
        
    
    def getNodeMapX(self,arry):
        y = 0
        for row in arry:
            x = 0
            for tile in row:
                if tile == '03' or tile == '04' or tile == '05' or tile =='17' or tile == '13' or tile == '20':
                    currentNode = self.FindNode((x,y))
                    tilesBehind = row[:x]
                    tilesFront = row[x+1:]
                    BN = self.checkXTiles(tilesBehind[::-1],x,y,False,False)
                    FN = self.checkXTiles(tilesFront,x,y,True,False)
                    currentNode.neighbours.update(BN)
                    currentNode.neighbours.update(FN)
                    
                x+=1
            y+=1
        return

    def getNodeMapY(self,arry):
        x = 0
        for column in arry:
            y = 0
            for tile in column:
                if tile == '03' or tile == '04' or tile == '05' or tile =='17' or tile == '13' or tile == '20':
                    currentNode = self.FindNode((x,y))
                    tilesAbove = column[:y]
                    tilesBelow = column[y+1:]
                    AN = self.checkYTiles(tilesAbove[::-1],x,y,False,False)
                    BN = self.checkYTiles(tilesBelow,x,y,True,False)
                    currentNode.neighbours.update(AN)
                    currentNode.neighbours.update(BN)
                y += 1
            x += 1
        return
    
    def FindNode(self,pos):
        for Node in self.gNodes:
            if Node.pos == pos:
                return Node
   
           
    def checkXTiles(self,lst,x,y,flag,isPlayer):
        #check for player pos and see if node for all neighbouring node checks
        distance = 1
        d = {}
        for tile in lst:
            if tile == '03' or tile == '04' or tile == '05' or tile == '17' or tile == '20' or tile == '13':
                if isPlayer == True and tile == '13':
                    return d
                elif flag == False:
                    Node = self.FindNode((x-distance,y))
                    d[Node] = [distance, 'Left']
                elif flag == True:
                    Node = self.FindNode((x + distance,y))
                    d[Node] = [distance, 'Right']                
                return  d
            
            elif tile == '06' or tile == '07' or tile == '08' or tile == '09' or tile == '10' or tile == '11':
                return d
            distance += 1
        return d

    def checkYTiles(self,lst,x,y,flag,isPlayer):
        distance = 1
        d = {}
        for tile in lst:
            if tile == '03' or tile == '04' or tile == '05' or tile == '17' or tile == '20' or tile =='13':
                if isPlayer == True and tile == '13':
                    return d
                elif flag == False:
                    Node = self.FindNode((x,y-distance))
                    d[Node] = [distance, 'Up']
                elif flag == True:
                    Node = self.FindNode((x,y+ distance))
                    d[Node] = [distance , 'Down']
                
                return d
            elif tile == '06' or tile == '07'or tile == '08' or tile == '09' or tile == '10' or tile == '11':
                return d
            distance += 1
        return d
    
    
    
    def getPlayerPossibleMoves(self,player,arry,transposedArry):
        player.possibleMoves = []
        x = player.xTile
        y = player.yTile
        #to get the possible x moves
        row = arry[y]
        TilesBehind = row[:x]
        TilesFront = row[x+1:]
        BehindNode = self.checkXTiles(TilesBehind[::-1],x,y,False, True)
        FrontNode = self.checkXTiles(TilesFront,x,y,True,True)
        column = transposedArry[x]
        TilesAbove = column[:y]
        TilesBelow = column[y+1:]
        AboveNode = self.checkYTiles(TilesAbove[::-1],x,y,False,True)
        BelowNode = self.checkYTiles(TilesBelow,x,y,True,True)
        dic = {}
        dic.update(BehindNode)
        dic.update(FrontNode)
        dic.update(AboveNode)
        dic.update(BelowNode)
        for key in dic:
            player.possibleMoves.append(dic[key][1])
        
        
        return

    def checkDistanceFromNodes(self,ghost,arry,transposedArry):
        ghost.neighbours = {}
        x = ghost.xTile
        y = ghost.yTile
        if arry[y][x] == '03' or arry[y][x] == '04' or arry[y][x] == '05':
            for n in self.gNodes:
                if n.pos == (x,y):
                    ghost.NodeCameFrom = n
        row = arry[y]
        TilesBehind = row[:x]
        TilesFront = row[x+1:]
        BehindNode = self.checkXTiles(TilesBehind[::-1],x,y,False,False)
        FrontNode = self.checkXTiles(TilesFront,x,y,True,False)
        column = transposedArry[x]
        TilesAbove = column[:y]
        TilesBelow = column[y+1:]
        AboveNode = self.checkYTiles(TilesAbove[::-1],x,y,False,False)
        BelowNode = self.checkYTiles(TilesBelow,x,y,True,False)
        ghost.neighbours.update(BehindNode)
        ghost.neighbours.update(FrontNode)
        ghost.neighbours.update(AboveNode)
        ghost.neighbours.update(BelowNode)
        return


       
        
    
    def getTiles(self,object):
        for pos in self.PlayerTilePos:
            if object.rectangle.colliderect(pos[0]):
                object.setxTile(pos[1])
                object.setyTile(pos[2])
                return
        if isinstance(object,player):
            for pos in self.teleportPos:
                if object.rectangle.colliderect(pos[0]):
                    index = self.teleportPos.index(pos)
                    if index == 0:
                        object.setxTile(self.teleportPos[1][1] -1)
                        object.setyTile(self.teleportPos[1][2])
                    else:
                        object.setxTile(self.teleportPos[0][1] + 1)
                        object.setyTile(self.teleportPos[0][2])
                        object.isTeleport()
                        return

        for pos in self.gNodePos:
            if object.rectangle.colliderect(pos[0]):
                object.setxTile(pos[1])
                object.setyTile(pos[2])
                return
        return

    def drawHud(self,font,player):
        gameDisplay.blit(self.playerImage,(self.LifeImageCords[0],self.LifeImageCords[1]))
        score = font.render(str(player.score),1,(255,255,255))
        gameDisplay.blit(score,(self.scoreCords[0],self.scoreCords[1]))
        NoLives = font.render(("X "+ str(player.lives)),1,(255,255,255))
        gameDisplay.blit(NoLives,(self.LifeCords[0],self.LifeCords[1]))

    def DeathScreen(self,font):
        text = font.render("You Died",1,(255,255,255))
        gameDisplay.blit(text,(14*13 + 80,15*13 + 182))
        return

        

class gNode:
    def __init__(self,pos,canPlayerGo,isPlayer):
        self.pos = pos
        self.x = self.pos[0] * 13 + 110
        self.y = self.pos[1] *13 + 182
        self.image = pygame.image.load("Files/Sprites/Ghosts/Inky/bGR.png")
        self.neighbours = {}
        self.canPlayerGo = canPlayerGo
        self.isPlayer = isPlayer
        self.cost = 5 #This is calculated as the gNodes are calculated, which happens every frame as the player moves so it can lead to their location
        
        
        #Use is explained in the ghost Method below
        self.PreviousNode = None
        self.distanceFromStartNode = 0
        self.total = self.distanceFromStartNode + self.cost
        self.PreviousDirection = None
        self.rectangle = pygame.Rect(self.x,self.y,4,4)
    
    def setPreviousNode(self,previousNode):
        self.PreviousNode = previousNode
        return
    def setDistanceFromStartNode(self,distance):
        self.distanceFromStartNode = distance
        return
    def updateTotal(self):
        self.total = self.distanceFromStartNode + self.cost
        return
    def calculateCost(self,coins):
        nearRect = pygame.Rect(self.x,self.y,20,20)
        numberNear = coins.nearNode(nearRect)
        self.cost -= numberNear

        

        

    
        





class player:
    def __init__(self,imageR,imageL,imageU,imageD):
        self.CurrentImage = pygame.image.load(imageR)
        self.imageR = pygame.image.load(imageR)
        self.imageL = pygame.image.load(imageL)
        self.imageU = pygame.image.load(imageU)
        self.imageD = pygame.image.load(imageD)
        self.width = 13
        self.height = 13
        self.lives = 3
        self.x = None
        self.y = None
        self.xChange = 0
        self.yChange = 0
        self.noCCoins = 0
        self.noSCoins = 0
        self.rectangle = None
        self.xTile = None
        self.yTile = None
        self.movingLeft = False
        self.movingRight = False
        self.movingUp = False
        self.movingDown = False
        self.possibleMoves = []
        self.nextMove = None
        self.numberOfGhostsEaten = 0
        self.lastScoreLife = 0
        self.score = 0
    def draw(self):
        gameDisplay.blit(self.CurrentImage,(self.x,self.y))
    def move(self):
        self.x += self.xChange
        self.y += self.yChange
        if self.xChange > 0:
            self.CurrentImage = self.imageR
        elif self.yChange < 0:
            self.CurrentImage = self.imageU
        elif self.xChange < 0:
            self.CurrentImage = self.imageL
        elif self.yChange > 0:
            self.CurrentImage = self.imageD
        self.rectangle = pygame.Rect(self.x,self.y,self.height,self.width)
        return
    def setSpawn(self,x,y):
        self.x = x
        self.y = y
        self.rectangle = pygame.Rect(self.x,self.y,self.height,self.width)
        return
    def setxTile(self,x):
        self.xTile = x
        return
    def setyTile(self,y):
        self.yTile = y
        return

    def isTeleport(self):
        self.x = self.xTile*13 + 110
        self.y = self.yTile*13 + 182

    def wallHit(self):
        if self.yChange == -1:
            if 'Up' not in self.possibleMoves:
                self.yChange = 0
        if self.yChange == 1:
            if 'Down' not in self.possibleMoves:
                self.yChange = 0
        if self.xChange == 1:
            if 'Right' not in self.possibleMoves:
                self.xChange = 0
        if self.xChange == -1:
            if 'Left' not in self.possibleMoves:
                self.xChange = 0
        else:
            return
        return

    def checkNextMove(self):
        if self.nextMove in self.possibleMoves:
            if self.nextMove == 'Up':
                self.yChange = -1
                self.xChange = 0
            elif self.nextMove == 'Down':
                self.yChange = 1
                self.xChange = 0
            elif self.nextMove == 'Left':
                self.xChange = -1
                self.yChange = 0
            elif self.nextMove == 'Right':
                self.xChange = 1
                self.yChange = 0
            return

    def calculateScore(self):
        self.score = (self.noCCoins * 10) + (self.noSCoins * 100) + (self.numberOfGhostsEaten * 200)
        return
    
    def checkExtraLife(self): #Problem when score is a multiple of 10000 and player stays still/ gets no points
        if self.score != self.lastScoreLife:
            if self.score % 10000 == 0:
                self.lives += 1
                self.lastScoreLife = self.score
        return
   #to fix this I added another attribute where the last score is saved when the player recieved a life



        
        #def death(self):
        # or restart inital game loop
        # ghosts return to start
        #player returns to start
        # number of lives reduced by 1




class coin:
    def __init__(self,image,height,width,x,y,type,xTile,yTile):
        self.image = pygame.image.load(image)
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.type = type
        self.present = True
        self.xTile = xTile
        self.yTile = yTile
        self.rectangle = pygame.Rect(self.x,self.y,self.height,self.width)
    def draw(self,image):
        gameDisplay.blit(self.image,(self.x,self.y))
    
    def delete(self):
        self.present = False
        self.image = pygame.image.load("Files/Sprites/nothing.png")
  






class ghost:
    def __init__(self,imageR,imageL,imageU,imageD,x,y):
        self.imageR = pygame.image.load(imageR)
        self.imageL = pygame.image.load(imageL)
        self.imageU = pygame.image.load(imageU)
        self.imageD = pygame.image.load(imageD)
        self.imageDR = pygame.image.load("Files\Sprites\Ghosts\DeadGhost\dGRight.png")
        self.imageDL = pygame.image.load("Files/Sprites/Ghosts/DeadGhost/dgLeft.png")
        self.imageDU = pygame.image.load("Files/Sprites/Ghosts/DeadGhost/dgUp.png")
        self.imageDD = pygame.image.load("Files/Sprites/Ghosts/DeadGhost/dgDown.png")
        self.imageV = pygame.image.load("Files/Sprites/Ghosts/DeadGhost/vghost.png")
        self.currentImage = self.imageR
        self.width = 13
        self.height = 13
        self.v = False
        self.dead = False
        self.xChange = 0
        self.yChange = 0
        self.x = x
        self.y = y
        self.xTile = None
        self.yTile = None
        self.rectangle = None
        self.neighbours = {}
        self.currentDirection = None
        self.previousDirection = None
        self.NodeCameFrom = None
  
    
    def move(self):
        self.x += self.xChange
        self.y += self.yChange
        
        if self.xChange > 0:
            if self.dead == False and self.v == False:
                self.currentImage = self.imageR
            elif self.v == True:
                
                self.currentImage = self.imageV
            else:
                self.currentImage = self.imageDR
        
        elif self.yChange < 0:
            if self.dead == False and self.v == False:
                self.currentImage = self.imageU
            elif self.v == True:
                
                self.currentImage = self.imageV
            else:
                self.currentImage = self.imageDU


        elif self.xChange < 0:
            if self.dead == False and self.v == False:
                self.currentImage = self.imageL
            elif self.v == True:
                
                self.currentImage = self.imageV
            else:
                self.currentImage = self.imageDL


        elif self.yChange > 0:
            if self.dead == False and self.v == False:
                self.currentImage = self.imageD
            elif self.v == True:

                self.currentImage = self.imageV
            else:
                self.currentImage = self.imageDD
        self.rectangle = pygame.Rect(self.x,self.y,self.height,self.width)
        return
    
    def draw(self):
        gameDisplay.blit(self.currentImage,(self.x,self.y))
    
    def isVulnerable(self):
        self.v = True
        self.currentImage = self.imageV
        return
    def invulnerable(self):
        self.v = False
        if self.dead == False:
            self.currentImage = self.imageR
        else:
            self.currentImage = self.imageDR
        return
    
    def setxTile(self,x):
        self.xTile = x
        return
    def setyTile(self,y):
        self.yTile = y
        return
    
    ###Think error is that it still checks visited Nodes so is endless.
    def FindShortestPath(self,level,targetNode):
        visitedNodes = []
        unvistedNodes = level.gNodes
        #print(unvistedNodes)
        pq = priorityQueue() # makes a priority Queue
        #The ghosts does not act as a node to other Nodes, neighbours holds the nodes around the ghost. - to limit other ghosts following the same path
        for n in self.neighbours:
            #print(self.neighbours)
            directionFromStartNode = self.neighbours[n][1]
            #print(directionFromStartNode)#Points to the direction of the neighbouring Node, from the one we are looking at
            if n == targetNode:#Check if the neighbouring node is the target Node and return the direction the ghost has to go to get there
                direction = directionFromStartNode
                return direction
            
            else:
                n.setDistanceFromStartNode(self.neighbours[n][0]) #Nodes have a DistanceFromStartNode attribute, So the priority queue can be sorted
                n.updateTotal() #Function that adds the cost and distanceFromStartNode for the A* algorithm
                #print(directionFromStartNode)
                n.PreviousDirection = directionFromStartNode #Sets the previous Direction so the ghost can move towards if it is the first Node in the path
                #print(n)
                #print(n.total)
                pq.insertNode(n) #inserts a Node in the sorted order it should be in
        while True:
            pq.bubbleSort() #the list is sorted
            #print("Visited Nodes")

            #print(visitedNodes)
            #print("In queue")
            #print(pq.queue)
            
            top = pq.getFirstValue() #pops the first value in the queue
           # #print("Details about Top")
            #print(top)
            #print(top.neighbours)
            #print(top.PreviousNode)
            #level.rendermap(gameDisplay)
            #self.printPath(top,level)
            if top == targetNode: #If the top is the target Node that means the shortest distance has been achieved
                #print("Found")
                direction = self.backTrack(top)#Should return the .PreviousDirection of the First Node in the path so the ghost can move toward it
                return direction
            elif top in visitedNodes: #Checks if the top has already been looked at
                #print("Already Seen")
                continue
            else:
                for node in top.neighbours:#looks at the neighbours of the top Node in the queue
                    #print("All Nodes in queue")
                    #print(pq.queue)
                    #print(node)
                    distance = top.neighbours[node][0]#Returns the distance of the Node from the top node as it is a dictionary
                    if node == self.NodeCameFrom or node == top.PreviousNode:
                        continue
                    if node in pq.queue:#Checks if there is an instance of the node already in the queue
                        #print("Already In queue")
                        index = pq.queue.index(node)
                      
                        if pq.queue[index].distanceFromStartNode > top.distanceFromStartNode + distance:#We compare the current distances of the Node to the newly calculated distance
                            #print("Path is Shorter")
                            #print("Change")
                            pq.queue[index].distanceFromStartNode = top.distanceFromStartNode + distance #Changes the distance
                            pq.queue[index].updateTotal()#Updates total to the smaller value
                            pq.queue[index].PreviousNode = top # sets the pointer to the Node it came from
                        
                        else: #If the path is longer then the route isn't good
                            #print("Path is longer")
                            continue
                   
                       
                    else:        #Otherwise add the node to the queue to wait to be looked at
                        node.setDistanceFromStartNode(top.distanceFromStartNode + distance) #sets the distance from start point
                        node.updateTotal()#updates total for A*
                        node.PreviousNode = top #sets the pointer as the Node that lead us here
                        pq.insertNode(node)
                        #print("Inserterd into Queue")
                    
                visitedNodes.append(top) #Then we append to be compared on the next iterations to see if we have already done the calculations to prevent it running forever
            
            


    def removeOppositeDirectionNode(self):
        node = None
        oppositeDirection = self.notTurnBack()
        for n in self.neighbours:
            if self.neighbours[n][1] == oppositeDirection:
                node = n
        self.neighbours.pop(node,None)
        return
    def removeNodeCameFrom(self):
        node = None
        for n in self.neighbours:
            if self.NodeCameFrom == n:
                node = n
        self.neighbours.pop(node,None)

    def printPath(self,node,level):
        if node.PreviousNode == None:
            return
        else:
            pNode = node.PreviousNode
            pNodeCord = ((pNode.pos[0]*13 + 110),(pNode.pos[1]*13 +182))
            nodeCord =((node.pos[0]*13 +110),(node.pos[1]*13 + 182))
            pygame.draw.line(gameDisplay,(255,0,0),pNodeCord,nodeCord,5)
            return self.printPath(node.PreviousNode,level)
        

    def backTrack(self,node):#recursive program to go through from the last node of the path to the first
        #print(node.PreviousNode)
        
        if node.PreviousNode == None:#First node doesn't have a pointer so return the direction the ghost needs to move in
            #print("This is the Node we started with")
            #print(node)
           # print(node.PreviousDirection)
            direction = node.PreviousDirection
            #print(direction)
            return direction
        
        else:
            return self.backTrack(node.PreviousNode)
    
            
            
            
    #def randomMove (self):
    #    nodes = self.neighbours
    #    lst = list(nodes.values())
    #    oppositeDirection = self.notTurnBack()
    #    for node in lst:
    #        if node[1] == oppositeDirection:
    #            lst.remove(node)
    #    if len(lst) == 1:
    #        direction = lst[0][1]
    #    else:
    #        index = random.randint(0,(len(lst) -1))
    #        direction = lst[index][1]
    #    if direction == 'Up':
    #        self.yChange = -1
    #        self.xChange = 0
    #    if direction == 'Down':
    #        self.yChange = 1
    #        self.xChange = 0
    #    if direction == 'Left':
    #        self.xChange = -1
    #        self.yChange = 0
    #    if direction == 'Right':
    #        self.xChange = 1
    #        self.yChange = 0
    #    self.currentDirection = direction
    #    return
    
    def findPlayer(self,level):
        self.xChange = 0
        self.yChange = 0
        self.removeOppositeDirectionNode()
        self.removeNodeCameFrom()
        directiontoHeadIn = self.FindShortestPath(level,level.playerNode)
        return self.returnDirectionToHeadIn(directiontoHeadIn)
        
    def decideMovement(self,player,level):
        if self.dead == True:
            if self.checkIsHome(level) == True:
                self.revive()
                return
            else:
                self.FindPathHome(level)
                return
        else:
            self.findPlayer(level)
            return


    def returnDirectionToHeadIn(self,direction):
        self.currentDirection = direction
        if direction == 'Up':
            self.yChange = -1
        
        elif direction == 'Down':
            self.yChange = 1
        
        elif direction == 'Left':
            self.xChange = -1
        
            
        elif direction == 'Right':
            self.xChange = 1
        return
        
        
    def setSpawn(self,x,y,xTile,yTile):
        self.x = x
        self.y = y
        self.rectangle = pygame.Rect(self.x,self.y,self.height,self.width)
        self.setxTile(xTile)
        self.setyTile(yTile)
        return
    
    def notTurnBack(self):
        if self.currentDirection == 'Up':
            oppositeDirection = 'Down'
        elif self.currentDirection == 'Down':
            oppositeDirection = 'Up'
        elif self.currentDirection == 'Left':
            oppositeDirection = 'Right'
        elif self.currentDirection == 'Right':
            oppositeDirection = 'Left'
        else:
            return
        return oppositeDirection

    def checkCollidePlayer(self,player,level):
        if player.rectangle.colliderect(self.rectangle) == True:
            if self.v == True:
                level.ghostEaten = True
                level.recentGhostDeath = self
                player.numberOfGhostsEaten += 1
                self.death(level)
                return True
            elif self.dead == True:
                return
            else:
                player.lives -= 1
                return
            return True
           #else:
           #    restart game loop
  
      
       #Find way back to home then return to normal state
   #def findPath():
   #    finds the path to a target from where it is currently located
   
       

   #def vulnerable(self):
       #display vulnerable image
       #run away from player
       #lasts 5 seconds or 300 frames      
        
    def death(self,level):
        self.dead = True
        self.v = False
        return

           
    def revive(self):
        self.dead = False
        self.currentImage = self.imageR
        #self.previousDirection = None
        #self.NodeCameFrom = None
        #self.currentDirection = None
        return
       
       
    def FindPathHome(self,level):
        self.xChange = 0
        self.yChange = 0
        self.removeOppositeDirectionNode()
        self.removeNodeCameFrom()
        directionToHeadIn = self.FindShortestPath(level,level.ghostHomeNode)
        return self.returnDirectionToHeadIn(directionToHeadIn)

    def checkIsHome(self,level):
        for rect in level.homeTiles:
            if self.rectangle.colliderect(rect) == True:
                self.revive()
        return
    def isDead(self):
        return self.dead

    def setDead(self,Bool):
        self.dead = Bool
        return
       
       #display image of death
        #find route back home
        #when home return to orignial state 

def findOppositeDirection(direction):
    if direction == 'Up':
        oppositeDirection = 'Down'
    elif direction == 'Down':
        oppositeDirection = 'Up'
    elif direction == 'Left':
        oppositeDirection = 'Right'
    elif direction == 'Right':
        oppositeDirection = 'Left'


class ghosts:
    def __init__(self,lst):
        self.ghosts = lst

    def ShouldBeInvulnerable(self):
        for g in self.ghosts:
            g.invulnerable()
    def setSpawns(self,x,y,xTile,yTile):
        for g in self.ghosts:
            g.setSpawn(x,y,xTile,yTile)

    def checkDistanceFromNodes(self,arry,transposedArry,level):
        for g in self.ghosts:
            level.checkDistanceFromNodes(g,arry,transposedArry)
        return
    
    def checkCollidePlayer(self,player):
        for g in self.ghosts:
            g.checkCollidePlayer(player)
        return
    
    def ShouldBeVulnerable(self):
        for g in self.ghosts:
            if g.dead == False:
                g.isVulnerable()
        return
# Each key will have a distance/value and the last node they visited

class priorityQueue:
    def __init__(self):
        self.queue = []
    
    # error created by passing parameters ### To talk about in testing
    def insertNode(self,Node):
        
        if len(self.queue) == 0:
            self.queue.append(Node)
            #print("List Empty, placed in first")
            return
        
        else:
            for n in self.queue:
                index = self.queue.index(n)
                
                if n.total > Node.total : #Sees if the total of the new Node is less than the total of the node in that position
                    self.queue.insert(index,Node)#Inserts at the index location and moves the trailing elements one along  ###  as Node is passed as n from previous function, it didnt work ### To talk about in testing
                    return

                elif index == len(self.queue) - 1: #If at the end of the queue
                    self.queue.append(Node)
                    #print("longest path")
                    return
                else:
                    continue
        return
    
    def getFirstValue(self):#pops the first value
        return self.queue.pop(0)
    
    def insertionSort(self):#an insertion sort according to the total of each Node in queue
        
        for index in range(1,len(self.queue)):
            currentValue = self.queue[index]
            currentTotal= self.queue[index].total
            currentPosition = index
            previousTotal = self.queue[index -1].total
            
            while currentPosition > 0 and currentTotal < previousTotal:
                self.queue[currentPosition] = self.queue[currentPosition -1]
                currentPosition -= 1
            self.queue[currentPosition] = currentValue
        return
    def bubbleSort(self):
        for i in range(len(self.queue)):
            for j in range(len(self.queue) -1):
                if self.queue[j].total > self.queue[j+1].total:
                    self.queue[j],self.queue[j+1] = self.queue[j+1],self.queue[j]
        return

                


 



#Linked list

class Node:
    def __init__(self,data):
        self.data = data
        self.pointer = None
    def render(self):
        self.data.draw(self.data)


class LinkedList:
    def __init__(self):
        self.first = None
        self.size = 0
    def draw(self,Node):
        Node.render()
        if Node.pointer == None:
            return
        else:
            self.draw(Node.pointer)
    def isEmpty(self):
        if self.first == None:
            return True
    
    def addNode(self,Node,newNode):
        if Node == None:
            self.first = newNode
            self.size += 1
            return
        elif Node.pointer == None:
            Node.pointer = newNode
            self.size += 1
            return
        else:
            self.addNode(Node.pointer,newNode)
    
    def deleteNode(self,Node,TargetNode,prevNode):
        if TargetNode == self.first:
            self.first = Node.pointer
            Node = None
            return
        elif Node == TargetNode:
            prevNode.pointer = Node.pointer
            return
        elif Node.pointer == None:
            return
        else:
            self.deleteNode(Node.pointer,TargetNode,Node)
    
    def checkCollide(self,Node,player,ghosts,coins,level):
        if playerCollideCoin(player,Node.data,coins,ghosts,level) == True:
            self.deleteNode(self.first,Node,None)
        elif Node.pointer == None:
            return
        else:
            self.checkCollide(Node.pointer,player,ghosts,coins,level)
    def nearNode(self,rect):
        numberNear = 0
        blip = self.first
        while blip != None:
            if blip.data.rectangle.colliderect(rect) == True:
                numberNear += 1
            blip = blip.pointer
        return numberNear




               
   



#def collision(objA,objB):
   # if objA.y < (objB.y + objB.height):
    #    if objA.x > objB.x and objA.x < (objB.x + objB.width) or (objA.x + objA.width) > objB.x and (objA.x + objA.width) < (objB.x + objB.width):
            #return True
   # else:
    #    return False


def playerCollideCoin(player,coin,coins,ghosts,level):
    if player.rectangle.colliderect(coin.rectangle) == True:
        if coin.type == 'n':
            player.noCCoins += 1
            level.numberOfCoins -= 1
            return True
        elif coin.type == 's':
            player.noSCoins += 1
            level.numberOfCoins -= 1
            #threadOne = threading.Thread(target = vulnerable, args = (Blinky,player,level))
            #threadTwo = threading.Thread(target = vulnerable, args = (Inky,player,level))
            #threadThree = threading.Thread(target = vulnerable, args = (Pinky,player,level))
            #threadFour = threading.Thread(target = vulnerable, args =(Clyde,player,level))
            #threadOne.start()
            #threadTwo.start()
            #threadThree.start()
            #threadFour.start()
            return True
        else:
            return
        



#Thread timer instead of all this bs
#def vulnerable(ghost,player,level):
#    startT = time.time()
#    timer = 0
#    while timer !=5:
#        if ghost.checkCollidePlayer(player,level) == True:
#            ghost.setDead(True)
#            ghost.invulnerable()
#            break

#        ghost.isVulnerable()
#        #Create as much distance as possible from the player
#        currentTime = time.time()
#        timer = round(currentTime-startT)
    
#    if ghost.isDead() == True:
#        while True:
#            ghost.death(level)

#    ghost.invulnerable()
#    return

def playerCollideGhost(player,ghosts):
    for g in ghosts:
        if player.rectangle.colliderect(g.rectangle):
            if g.v == True:
                g.death()
                return False
            else:
                return True

def timer(ghosts):
    startT = time.time()
    timer = 0
    while timer != 5:
        ghosts.ShouldBeVulnerable()
        currentTime = time.time()
        t = round(currentTime-startT)
    ghosts.Invulnerable()
    return






#def playerCollision(player,objB,ghosts,coins): # change for collision with ghost or coins
#    if player.y > objB.y and player.y < (objB.y + objB.height) or (player.y + player.height) > objB.y and (player.y + player.height) < (objB.y + objB.height):
#        if player.x > objB.x and player.x < (objB.x + objB.width) or (player.x + player.width) > objB.x and (player.x + player.width) < (objB.x + objB.width):
            
#            if isinstance(objB,ghost):
#                if objB.v == True:
#                    thread = threading.Thread(target = ghost.death, args = (objB,))
#                    thread.start()
#               #else:
#                    #player.death()
#                    #do function of restart round
#            elif isinstance(objB,coin) and objB.present == True:
#                if objB.type == 'n':
#                    player.noCCoins += 1
#                    coins.deleteNode(coins.first,objB,None)
#                    return True
#                elif objB.type == 's':
#                    player.noSCoins += 1
#                    coins.deleteNode(coins.first,objB,None)
#                    thread = threading.Thread(target = vulnerable, args = (ghosts,))
#                    thread.start()
#                    return True
#    else:
#        return False





displayWidth = 800
displayHeight = 600
gameDisplay = pygame.display.set_mode((displayHeight,displayWidth))

#colours
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
pygame.display.set_caption('Pacman')

clock = pygame.time.Clock()





def gameLoop():
    coins = LinkedList()
    maze = [['06','10','10','10','10','10','10','10','10','10','10','10','10','08','06','10','10','10','10','10','10','10','10','10','10','10','10','08'],
 ['11','03','01','01','01','01','03','01','01','01','01','01','03','11','11','03','01','01','01','01','01','03','01','01','01','01','03','11'],
 ['11','01','06','10','10','08','01','06','10','10','10','08','01','11','11','01','06','10','10','10','08','01','06','10','10','08','01','11'],
 ['11','02','11','00','00','11','01','11','00','00','00','11','01','11','11','01','11','00','00','00','11','01','11','00','00','11','02','11'],
 ['11','01','07','10','10','09','01','07','10','10','10','09','01','07','09','01','07','10','10','10','09','01','07','10','10','09','01','11'],
 ['11','03','01','01','01','01','03','01','01','03','01','01','03','01','01','03','01','01','03','01','01','03','01','01','01','01','03','11'],
 ['11','01','06','10','10','08','01','06','08','01','06','10','10','10','10','10','10','08','01','06','08','01','06','10','10','08','01','11'],
 ['11','01','07','10','10','09','01','11','11','01','07','10','10','08','06','10','10','09','01','11','11','01','07','10','10','09','01','11'],
 ['11','03','01','01','01','01','03','11','11','03','01','01','03','11','11','03','01','01','03','11','11','03','01','01','01','01','03','11'],
 ['07','10','10','10','10','08','01','11','07','10','10','08','00','11','11','00','06','10','10','09','11','01','06','10','10','10','10','09'],
 ['00','00','00','00','00','11','01','11','06','10','10','09','00','07','09','00','07','10','10','08','11','01','11','00','00','00','00','00'],
 ['00','00','00','00','00','11','01','11','11','05','00','00','05','05','00','05','00','00','05','11','11','01','11','00','00','00','00','00'],
 ['00','00','00','00','00','11','01','11','11','00','06','10','10','00','00','10','10','08','00','11','11','01','11','00','00','00','00','00'],
 ['10','10','10','10','10','09','01','07','09','00','11','00','19','19','19','00','00','11','00','07','09','01','07','10','10','10','10','10'],
 ['17','00','00','00','00','00','03','00','00','05','11','00','19','13','19','00','00','11','05','00','00','03','00','00','00','00','00','17'],
 ['10','10','10','10','10','08','01','06','08','00','11','00','19','19','19','00','00','11','00','06','08','01','06','10','10','10','10','10'],
 ['00','00','00','00','00','11','01','11','11','00','07','10','10','10','10','10','10','09','00','11','11','01','11','00','00','00','00','00'],
 ['00','00','00','00','00','11','01','11','11','05','00','00','00','00','00','00','00','00','05','11','11','01','11','00','00','00','00','00'],
 ['00','00','00','00','00','11','01','11','11','00','06','10','10','10','10','10','10','08','00','11','11','01','11','00','00','00','00','00'],
 ['06','10','10','10','10','09','01','07','09','00','07','10','10','08','06','10','10','09','00','07','09','01','07','10','10','10','10','08'],
 ['11','03','01','01','01','01','03','01','01','03','01','01','03','11','11','03','01','01','03','01','01','03','01','01','01','01','03','11'],
 ['11','01','06','10','10','08','01','06','10','10','10','08','01','11','11','01','06','10','10','10','08','01','06','10','10','08','01','11'],
 ['11','01','07','10','08','11','01','07','10','10','10','09','01','07','09','01','07','10','10','10','09','01','11','06','10','09','01','11'],
 ['11','04','01','03','11','11','03','01','01','03','01','01','03','15','00','03','01','01','01','01','01','03','11','11','03','01','04','11'],
 ['07','10','08','01','11','11','01','06','08','01','06','10','10','10','10','10','10','08','01','06','08','01','11','11','01','06','10','09'],
 ['06','10','09','01','07','09','01','11','11','01','07','10','10','08','06','10','10','09','01','11','11','01','07','09','01','07','10','08'],
 ['11','03','01','03','01','01','03','11','11','03','01','01','03','11','11','03','01','01','03','11','11','03','01','01','03','01','03','11'],
 ['11','01','06','10','10','10','10','09','07','10','10','08','01','11','11','01','06','10','10','09','07','10','10','10','10','08','01','11'],
 ['11','01','07','10','10','10','10','10','10','10','10','09','01','07','09','01','07','10','10','10','10','10','10','10','10','09','01','11'],
 ['11','03','01','01','01','01','01','01','01','01','01','01','03','01','01','03','01','01','01','01','01','01','01','01','01','01','03','11'],
 ['07','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','09']]
    
    
    level = map(maze)
    
    Font = pygame.font.SysFont("Times New Roman", 12)
    DeathFont = pygame.font.SysFont("Times New Roman", 22)
    frameCount = 0
    currentFrame = 0
    playerOne = player("Files/Sprites/PlayerSprites/PR.png","Files/Sprites/PlayerSprites/PL.png","Files/Sprites/PlayerSprites/PU.png","Files/Sprites/PlayerSprites/PD.png")
    
    
    

    Blinky = ghost("Files/Sprites/Ghosts/Blinky/rGR.png","Files/Sprites/Ghosts/Blinky/rGL.png","Files/Sprites/Ghosts/Blinky/rGU.png","Files/Sprites/Ghosts/Blinky/rGD.png",300,380)
    
    Inky = ghost("Files/Sprites/Ghosts/Inky/bGR.png","Files/Sprites/Ghosts/Inky/bGL.png","Files/Sprites/Ghosts/Inky/bGU.png","Files/Sprites/Ghosts/Inky/bGD.png",300,367)
    
    Pinky = ghost('Files/Sprites/Ghosts/Pinky/pGR.png','Files/Sprites/Ghosts/Pinky/pGL.png','Files/Sprites/Ghosts/Pinky/pGU.png','Files/Sprites/Ghosts/Pinky/pGD.png' ,200,200)
    Clyde = ghost("Files/Sprites/Ghosts/Clyde/yGR.png","Files/Sprites/Ghosts/Clyde/yGL.png","Files/Sprites/Ghosts/Clyde/yGU.png","Files/Sprites/Ghosts/Clyde/yGD.png",100,200)
    Ghosts = ghosts([Blinky,Inky,Pinky,Clyde])
    gameExit = False
    
    while playerOne.lives > 0:
        
        if level.nextLevel == True:
            print("hello")
            level.getCoins(coins)
            level.nextLevel = False

        level.getSpawns(playerOne,Ghosts)
        playerScoins = 0
        currentTime = 0
        timeEatenEnergiser = 0
        playersCurrentLives = playerOne.lives
        while not gameExit :
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True

                if playerOne.lives == 0:
                    gameExit = True
                
                #if event.type == pygame.MOUSEBUTTONUP:
                    #print(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if 'Left' in playerOne.possibleMoves:
                            playerOne.xChange = -1
                            playerOne.yChange = 0
                            playerOne.nextMove = None
                        else:
                            playerOne.nextMove = 'Left'
                    
                    elif event.key == pygame.K_RIGHT:
                        if 'Right' in playerOne.possibleMoves:
                            playerOne.xChange = 1
                            playerOne.yChange = 0
                            playerOne.nextMove = None
                        else:
                            playerOne.nextMove = 'Right'
                    
                        #if playerCollideMap(playerOne,level) == True:
                          # pass
                        #else:  
                    elif event.key == pygame.K_UP:
                        if 'Up' in playerOne.possibleMoves:
                            playerOne.xChange = 0
                            playerOne.yChange = -1
                            playerOne.nextMove = None
                        else:
                            playerOne.nextMove = 'Up'
                    
                    elif event.key == pygame.K_DOWN:
                        if 'Down' in playerOne.possibleMoves:
                            playerOne.xChange = 0
                            playerOne.yChange = 1
                            playerOne.nextMove = None
                        else:
                            playerOne.nextMove = 'Down'
                   
                        
                            #if playerCollideMap(playerOne,level) == True:
                            #pass
     
            currentTime =  pygame.time.get_ticks()       
            level.getNodeMapAll(playerOne,Ghosts,coins)
            coins.checkCollide(coins.first,playerOne,Ghosts,coins,level)
        
            if playerOne.noSCoins - playerScoins != 0:
                level.ShouldBeVulnerable = True
                timeEatenEnergiser = pygame.time.get_ticks()
                Ghosts.ShouldBeVulnerable()
                playerScoins += 1
            if currentTime - timeEatenEnergiser > 5000:
                Ghosts.ShouldBeInvulnerable()
            
        
            Blinky.checkCollidePlayer(playerOne,level)
            Blinky.decideMovement(playerOne,level)        
        
            Blinky.move()
        
            Inky.move()
       
            Pinky.move()
        
            Clyde.move()
            playerOne.checkNextMove()
            playerOne.move()

            level.getTiles(playerOne)
            level.getTiles(Blinky)
            level.getTiles(Inky)
            level.getTiles(Pinky)
            level.getTiles(Clyde)
            playerOne.wallHit()
            playerOne.calculateScore()
            playerOne.checkExtraLife()

        
        
        

            if coins.isEmpty() == True:
                level.nextLevel = True
                level.LevelNo += 1
                break
            #Draws all objects
            gameDisplay.fill(black)
            level.rendermap(gameDisplay)
            coins.draw(coins.first)
            playerOne.draw()    
            Blinky.draw()
            Inky.draw()
            Pinky.draw()
            Clyde.draw()
            if level.ghostEaten == True:
                pointsForEatingGhost = Font.render("200",1,(0,255,0))
                xCord = level.recentGhostDeath.x
                yCord = level.recentGhostDeath.y
                gameDisplay.blit(pointsForEatingGhost,(xCord,yCord))
                time.sleep(0.66)
                level.recentGhostDeath = None
                level.ghostEaten = False
            level.drawHud(Font,playerOne)
            if playersCurrentLives > playerOne.lives: # originally != would execute when gained life
                level.DeathScreen(DeathFont)
                pygame.display.update()
                time.sleep(1)
                break
            pygame.display.update()
            frameCount += 1
            currentFrame = frameCount
            clock.tick(60)










gameLoop()

pygame.quit()
quit()
#have a function for one of the ghosts where they look for the coins and move around there   
#Have a predicitve algorithm that will determine a most likely path of the player, based on the players moves that game: dictionary for every node or left and right
#Allow for the timer of vulnerability to change after each level
#Account system
#Menu screens


