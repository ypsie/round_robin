import numpy as np
import pandas as pd 

class RoundRobin():

    def __init__(self,players,teams):
        
        self.player_list = players
        self.player_count, _ = self.player_list.shape
        self.teams = teams
        
        
        self.player_dict = {}
        self.games = 1

        if self.player_count%2 == 1:
            bye = np.array(['Bye-week'])
            self.player_list = np.concatenate((self.player_list, [bye]))
            self.player_count += 1
        
        if (self.player_count - 1)*2 > len(self.teams):
            raise Exception("No. of teams must at least be > 2*(No. of players - 1)") 

    def print_players(self):
        print(self.player_list)
        
    def generate_schedule(self):
        #shuffle player list to randomly assign start player
        np.random.shuffle(self.player_list)

        #index where array gets flipped to create a circular array and to implement a behaviour like
        #  1 2 3  -->  1 6 2  -->  1 5 6
        #  6 5 4       5 4 3       4 3 2

        flip_index = self.player_count//2 - 1
        players = self.player_list
        first = players[0]
        rest = players[1:]
        rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
        players = np.concatenate(([first], rest))
        self.schedule = np.reshape(players, (2, len(players)//2))
        
        
        ################################################################
        # this loop implements the round robin behaviour with flipping, rolling etc
        # player count - 2 because the first round is already assigned
        for _ in range(self.player_count - 2):

            rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
            #print(rest)
            rest = np.roll(rest,1)
            #print(rest)
            rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
            #print(rest)
            players = np.concatenate(([first], rest))
            games = np.reshape(players, (2, len(players)//2))
            #print(games)
            self.schedule = np.concatenate((self.schedule, games))
        
        ################################################################
        
    def stack_csv(self, teams_assigned=True):
        rows, cols = self.schedule.shape
        # header = header = np.array([['Day','Player Home','Team Home','Home Score','Away Score','Away Team','Away Player']])
        header = np.array([['Spieltag','Heimspieler','Heimmannschaft','Heimtore','Auswärtstore','Auswärtsmannschaft','Auswärtsspieler']])
        day = 0
        if teams_assigned:
            for x in range(2):
                for row in range(0,rows-1, 2):
                    day += 1 
                    for col in range(cols):
                        if x == 0:
                            
                            temp = np.array([day,self.schedule[row][col], self.team_schedule_hin[row][col], ' ', ' ', self.team_schedule_hin[row+1][col], self.schedule[row+1][col]])
                            header = np.concatenate((header,[temp]))
                            #hinrunde
                        elif x == 1:
                            temp = np.array([day, self.schedule[row+1][col], self.team_schedule_rueck[row+1][col],' ', ' ', self.team_schedule_rueck[row][col],self.schedule[row][col]])
                            header = np.concatenate((header,[temp]))

        self.csv_stack = header                            




    def write_csv(self):
        pd.DataFrame(self.csv_stack).to_csv("schedule.csv",header=None,index=None)

    def print_schedule(self, teams_assigned=False):
        rows, cols = self.schedule.shape
        if not teams_assigned:
            for _ in range(2):
                for row in range(0,rows-1, 2):
                    print(f'------------------\nSpieltag\t{self.games}\n------------------\n')
                    for col in range(cols):
                        print(self.schedule[row][col], ' vs. ', self.schedule[row+1][col],'\n')
                    self.games +=1
        else:
            for _ in range(2):
                for row in range(0,rows-1, 2):
                    print(f'------------------\nSpieltag\t{self.games}\n------------------\n')
                    for col in range(cols):
                        if self.games > rows//2:
                            print(self.schedule[row][col], ' w. ', self.team_schedule_rueck[row][col], ' vs. ', self.schedule[row+1][col],' w. ', self.team_schedule_rueck[row+1][col], '\n')
                        else:
                            print(self.schedule[row][col], ' w. ', self.team_schedule_hin[row][col], ' vs. ', self.schedule[row+1][col],' w. ', self.team_schedule_hin[row+1][col], '\n')
                    self.games +=1


    def assign_teams_once(self):
        debug = 1
        rows, cols = self.schedule.shape
        # assign empty array for the team schedule
        team_schedule = [[' '*10 for _ in range(cols)] for _ in range(rows)]

        # empty numpy array for first round
        self.team_schedule_hin = np.array(team_schedule)
        
        # empty numpy array for first round
        self.team_schedule_rueck = np.array(team_schedule)

        # create a dict containing the players as keys() and the available teams as in a list as values
        # this is done to keep track of remaining teams for each player
        for i in range(len(self.player_list)):
                    self.player_dict[self.player_list[i][0]] = self.teams
        
        for runde in range(2):
            # since this is a two round robin tournament if the first round is already assigned
            # the remaining teams for each player are assigned to a new dict. If in the end there is no
            # compatible merge of players/teams, only the second half gets assigned again

            if runde == 1:
                player_dict_second_half = self.player_dict.copy()

            done = False
            while not done:
                done = True

                # iterate through the already built schedule, pick a player on a specific gameday, test if this player has non-picked
                # teams (gameday) available. If he/she has: assign a randomly chosen team to the specific player/game
                # if not (len(intersect == 0)): start this process all over again 
                for row in range(0,rows-1, 2):
                    team_list = self.teams
                    for col in range(cols): 
                        home_player = self.schedule[row][col]
                        intersect = np.intersect1d(team_list.flatten(),self.player_dict[home_player].flatten())
                        if intersect.size == 0:
                            print('Round:', runde, 'Debug:', debug)
                            debug += 1 
                            done = False
                            if runde == 0:
                                for i in range(len(self.player_list)):
                                    self.player_dict[self.player_list[i][0]] = self.teams
                            elif runde == 1:
                                self.player_dict = player_dict_second_half.copy()
                            continue
                        
                        pick_home = np.random.choice(intersect)
                        
                        if runde == 0:
                            self.team_schedule_hin[row][col] = pick_home
                        elif runde == 1:
                            self.team_schedule_rueck[row][col] = pick_home

                        team_list = np.delete(team_list, np.where(team_list == pick_home)[0])
                        self.player_dict[home_player]= np.delete(self.player_dict[home_player], np.where(self.player_dict[home_player] == pick_home)[0])

                        away_player = self.schedule[row+1][col]
                        intersect = np.intersect1d(team_list.flatten(),self.player_dict[away_player].flatten())
                        if intersect.size == 0:
                            done = False
                            print('Round:', runde, 'Debug:', debug)
                            debug += 1
                            if runde == 0:
                                for i in range(len(self.player_list)):
                                    self.player_dict[self.player_list[i][0]] = self.teams
                            elif runde == 1:
                                self.player_dict = player_dict_second_half.copy()
                            continue

                        pick_away = np.random.choice(intersect)

                        if runde == 0:
                            self.team_schedule_hin[row+1][col] = pick_away
                        elif runde == 1:
                            self.team_schedule_rueck[row+1][col] = pick_away


                        team_list = np.delete(team_list, np.where(team_list == pick_away)[0])
                        self.player_dict[away_player]= np.delete(self.player_dict[away_player], np.where(self.player_dict[away_player] == pick_away)[0])
                        

players = np.array([['Bensteiger'],['Jonas'],['Yannik'],['Yps'],['Diet'],['Maxi'],['Max Powers'],['Micha'],['Andi'],['David'] ])
teams = np.array([['Bayern'],['Dortmund'],['Leverkusen'],['Schalke'],['Hoffenheim'],['Leipzig'],['Stuttgart'],['Freiburg'],['Gladbach'],['Augsburg'],['Union'],['Hertha'],['Bremen'],['Frankfurt'],['Wolfsburg'],['Köln'],['Arminia'],['Mainz']])
if __name__ == '__main__':
    
    turnier = RoundRobin(players=players, teams=teams)
    turnier.generate_schedule()
    

    turnier.assign_teams_once()
    turnier.print_schedule(True)
    turnier.stack_csv()
    turnier.write_csv()
    
    #print(turnier.schedule.shape)

