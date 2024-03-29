#!/usr/bin/env python
#version 1.3
imageCache = 1.9

import web
import time
import collections
import operator
import math
import os
import bcrypt
import requests
import dateutil.parser
from os.path import join, dirname, isfile
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#web.config.debug = False

db = web.database(dbn='postgres', user=os.environ.get('DATABASE_USER'), pw=os.environ.get('DATABASE_PASSWORD'), db=os.environ.get('DATABASE_NAME'))

urls = (
	'/', 'index',
	'/login', 'login',
	'/logout', 'logout',
	'/admin/add', 'add',
	'/admin/addscore', 'addscore',
	'/admin/addscoresubmit', 'addscoresubmit',
	'/standings', 'standings',
	'/scores', 'scores',
	'/statistics', 'statistics',
	'/teams', 'teams',
	'/news', 'news',
	'/schedule', 'schedule',
	'/preview', 'preview',
	'/game', 'game',
	'/history', 'history',
	'/signup', 'signup',
	'/admin/addgame', 'addgame',
	'/admin/gameselect', 'gameselect',
	'/admin/teamselect', 'teamselect',
	'/admin/teamedit', 'teamedit',
	'/admin/teameditsubmit', 'teameditsubmit',
	'/admin/teamadd', 'teamadd',
	'/admin/teamaddsubmit', 'teamaddsubmit',
	'/admin/teamdeletesubmit', 'teamdeletesubmit',
	'/admin/playerselect', 'playerselect',
	'/admin/playeredit', 'playeredit',
	'/admin/playereditsubmit', 'playereditsubmit',
	'/admin/playeradd', 'playeradd',
	'/admin/playeraddsubmit', 'playeraddsubmit',
	'/admin/playerdeletesubmit', 'playerdeletesubmit',
	'/admin/scheduleselect', 'scheduleselect',
	'/admin/scheduleedit', 'scheduleedit',
	'/admin/scheduleeditsubmit', 'scheduleeditsubmit',
	'/admin/scheduledeletesubmit', 'scheduledeletesubmit',
	'/admin/scheduleadd', 'scheduleadd',
	'/admin/scheduleaddsubmit', 'scheduleaddsubmit',
	'/admin/scheduleupload', 'scheduleupload',
	'/admin/scheduleuploadsubmit', 'scheduleuploadsubmit',
	'/admin/newsselect', 'newsselect',
	'/admin/newsedit', 'newsedit',
	'/admin/newsadd', 'newsadd',
	'/admin/newsaddsubmit', 'newsaddsubmit',
	'/admin/newseditsubmit', 'newseditsubmit',
	'/admin/newsdeletesubmit', 'newsdeletesubmit',
	'/admin/seasonselect', 'seasonselect',
	'/admin/seasonadd', 'seasonadd',
	'/admin/seasonedit', 'seasonedit',
	'/admin/seasoneditsubmit', 'seasoneditsubmit',
	'/admin/seasonaddsubmit', 'seasonaddsubmit',
	'/admin/seasoncurrentsubmit', 'seasoncurrentsubmit',
	'/admin/historyselect', 'historyselect',
	'/admin/historyadd', 'historyadd',
	'/admin/historyaddsubmit', 'historyaddsubmit',
	'/admin/historyedit', 'historyedit',
	'/admin/historyeditsubmit', 'historyeditsubmit',
	'/admin/userselect', 'userselect',
	'/admin/useradd', 'useradd',
	'/admin/useraddsubmit', 'useraddsubmit',
	'/admin/userdeletesubmit', 'userdeletesubmit',
	'/maxflowsubmit', 'maxflowsubmit',
)
web.config.session_parameters['cookie_path'] = '/'
web.config.session_parameters['ignore_change_ip'] = False

app = web.application(urls, locals())
store = web.session.DiskStore('sessions')

if web.config.get('_session') is None:
	session = web.session.Session(app, store, initializer = {'logged': False, 'username': '', 'privilege': 0})
	web.config._session = session
else:
	session = web.config._session

def create_render(privilege):
	#if session.logged == True:
		#if privilege == 1:
			#render = web.template.render('templates/', base='baselight', globals={ 'str': str, 'int':int, 'time':time, 'collections':collections, 'unicode':unicode, 'operator':operator, 'sorted':sorted, 'round':round})
		#elif privilege == 2:
			#render = web.template.render('templates/', base='base', globals={ 'str': str, 'int':int, 'time':time, 'collections':collections, 'unicode':unicode, 'operator':operator, 'sorted':sorted, 'round':round, 'context': session})
	#else:
	render = web.template.render('templates/', base='baseguest', globals={ 'str': str, 'int':int, 'time':time, 'dateutil':dateutil.parser, 'collections':collections, 'unicode':unicode, 'operator':operator, 'sorted':sorted, 'round':round, 'context': session, 'sort_standings':sort_standings, 'multikeysort':multikeysort, 'imageCache':imageCache })
	return render

def notfound():
	season_current = db.select('season', where="current = 't'")[0]
	i = dict(season=season_current.year)
	teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
	scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
	render = create_render(session.privilege)
	return web.notfound(render.notfound(teamsdb, scheduledb))
	
app.notfound = notfound

class notfound:
	def GET(self):
		raise web.notfound()

def internalerror():
	season_current = db.select('season', where="current = 't'")[0]
	i = dict(season=season_current.year)
	teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
	scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
	render = create_render(session.privilege)
	return web.internalerror(render.internalerror(teamsdb, scheduledb))

app.internalerror = internalerror

class internalerror:
	def GET(self):
		raise web.internalerror()

class index:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		newsdb = db.select('news', order="posted DESC", limit=4)
		scoresdb = db.select('schedule', i, where="EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL", order="date DESC, time DESC", limit="8").list()
		upcoming = db.select('schedule', i, where="EXTRACT(YEAR FROM date) = $season AND team1score IS NULL", order="date, time", limit="8").list()
		teams_list = db.select('standings', i, order="league, shortname", where="season=$season").list()

		pointsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 1;", vars=i).list()
		sacksdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 1;", vars=i).list()
		interceptionsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 1;", vars=i).list()
		tdpsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 1;", vars=i).list()
		pointsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 1;", vars=i).list()
		sacksdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 1;", vars=i).list()
		interceptionsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 1;", vars=i).list()
		tdpsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype='reg') m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 1;", vars=i).list()
		
		instagram_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
		payload = {'access_token': instagram_token, 'fields': 'id,media_type,media_url,username,timestamp,thumbnail_url,permalink,caption'}
		media = requests.get('https://graph.instagram.com/me/media', params=payload)
		render = create_render(session.privilege)
		return render.index(teamsdb, scheduledb, newsdb, media.json(), pointsdbmen, sacksdbmen, interceptionsdbmen, tdpsdbmen, pointsdbwomen, sacksdbwomen, interceptionsdbwomen, tdpsdbwomen, scoresdb, teams_list, season_current.year, upcoming)

class signup:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i=dict(season = season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		
		render = create_render(session.privilege)
		return render.signup(teamsdb, scheduledb)

class login:
	def POST(self):
		username, password = web.input().username, web.input().password
		ident = db.select('users', where='username=$username', vars=locals())[0]
		if bcrypt.checkpw(password.encode('utf8'), ident['password'].encode('utf8')):
			session.logged = True
			session.privilege = ident['privilege']
			session.username = ident['username']
			render = create_render(session.privilege)
			raise web.seeother('/')
		else:
			return "Wrong username or password"

class logout:
	def POST(self):
		session.kill()
		session.logged = False
		render = create_render(session.privilege)
		raise web.seeother('/')

class add:
	def POST(self):
		d = web.input(gameid=[], playerid=[], gameplayed=[], touchdowns=[], tdpass=[], oneconvert=[], twoconvert=[], rouge=[], safety=[], interception=[], sack=[], season=[])
		keys = d.keys()
		if session.logged == True:
			vals = zip(*[d[k] for k in keys])
			l = [dict(zip(keys, v)) for v in vals]
			for p in l:
				statcheck = db.select('statistics', where="gameid = $gameid AND playerid = $playerid", vars=p)
				if not statcheck:
					db.insert('statistics', **p)
				else:
					db.update('statistics', where="gameid = $gameid AND playerid = $playerid", vars=p, **p)
			#db.multiple_insert('statistics', values=l)
			gameid=d.gameid[0]
			raise web.seeother('/admin/addscore?gameid=' + gameid)
		else:
			return "You do not have permission to make this request"

class addscore:
	def GET(self):
		i = web.input(gameid=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i.season = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		game_data = db.select('schedule', i, where="gameid = $gameid AND EXTRACT(YEAR FROM date) = $season")[0]

		if game_data.teamlines_points_lost is None:
			game_data.teamlines_points_lost = 0

		team1id=db.query("select st.id FROM schedule AS sc, standings AS st where gameid = $gameid AND sc.team1 = st.shortname AND st.season= $season;", vars=i)[0]
		team2id=db.query("select st.id FROM schedule AS sc, standings AS st where gameid = $gameid AND sc.team2 = st.shortname AND st.season= $season;", vars=i)[0]
		
		i.team1id = team1id.id
		i.team2id = team2id.id

		team1_score = db.query("SELECT sum (i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS Score FROM (SELECT s.gameid, s.playerid, p.teamid, s.touchdowns, s.oneconvert, s.twoconvert, s.rouge, s.safety FROM statistics AS s, players AS p WHERE s.playerid=p.playerid AND s.gameid = $gameid AND p.teamid = $team1id) AS i;", vars=i)[0]
		team2_score = db.query("SELECT sum (i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS Score FROM (SELECT s.gameid, s.playerid, p.teamid, s.touchdowns, s.oneconvert, s.twoconvert, s.rouge, s.safety FROM statistics AS s, players AS p WHERE s.playerid=p.playerid AND s.gameid = $gameid AND p.teamid = $team2id) AS i;", vars=i)[0]

		render = create_render(session.privilege)
		if session.logged == True:
			return render.addscore(i.gameid, teamsdb, scheduledb, game_data, team1_score.score, team2_score.score)
		else:
			return "You do not have permission to access this page"

class addscoresubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.update('schedule', where="gameid = $gameid", vars=i, **i)
			game_data = db.select('schedule', i, where="gameid = $gameid")[0]
			season_current = db.select('season', where="current = 't'")[0]
			i.season=season_current.year
			team1wins = db.query("SELECT COUNT(*) FROM schedule WHERE (team1score > team2score AND team1 = $team1 AND EXTRACT(YEAR FROM date) = $season) OR (team2score > team1score AND team2 = $team1 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team1losses = db.query("SELECT COUNT(*) FROM schedule WHERE (team1score < team2score AND team1 = $team1 AND EXTRACT(YEAR FROM date) = $season) OR (team2score < team1score AND team2 = $team1 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team1ties = db.query("SELECT COUNT(*) FROM schedule WHERE (team2score = team1score AND team1 = $team1 AND EXTRACT(YEAR FROM date) = $season) OR (team2score = team1score AND team2 = $team1 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team1ptsfor = db.query("SELECT SUM(p.a) FROM (SELECT SUM(team1score) AS a FROM schedule WHERE (team1 = $team1 AND EXTRACT(YEAR FROM date) = $season) UNION ALL SELECT SUM(team2score) AS a FROM schedule WHERE (team2 = $team1 AND EXTRACT(YEAR FROM date) = $season)) p", vars=i)[0]
			team1ptsagainst = db.query("SELECT SUM(p.a) FROM (SELECT SUM(team1score) AS a FROM schedule WHERE (team2 = $team1 AND EXTRACT(YEAR FROM date) = $season) UNION ALL SELECT SUM(team2score) AS a FROM schedule WHERE (team1 = $team1 AND EXTRACT(YEAR FROM date) = $season)) p", vars=i)[0]
			team1gamesplayed = int(team1wins.count + team1losses.count + team1ties.count)
			team1pointslost = db.query("SELECT SUM(teamlines_points_lost) FROM schedule WHERE teamlines = $team1 AND EXTRACT(YEAR FROM date) = $season", vars=i)[0]
			if team1pointslost.sum is None:
				team1points = int(team1wins.count*2 + team1ties.count)
			else:
				team1points = int(team1wins.count*2 + team1ties.count - team1pointslost.sum)

			team2wins = db.query("SELECT COUNT(*) FROM schedule WHERE (team1score > team2score AND team1 = $team2 AND EXTRACT(YEAR FROM date) = $season) OR (team2score > team1score AND team2 = $team2 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team2losses = db.query("SELECT COUNT(*) FROM schedule WHERE (team1score < team2score AND team1 = $team2 AND EXTRACT(YEAR FROM date) = $season) OR (team2score < team1score AND team2 = $team2 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team2ties = db.query("SELECT COUNT(*) FROM schedule WHERE (team2score = team1score AND team1 = $team2 AND EXTRACT(YEAR FROM date) = $season) OR (team2score = team1score AND team2 = $team2 AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			team2ptsfor = db.query("SELECT SUM(p.a) FROM (SELECT SUM(team1score) AS a FROM schedule WHERE (team1 = $team2 AND EXTRACT(YEAR FROM date) = $season) UNION ALL SELECT SUM(team2score) AS a FROM schedule WHERE (team2 = $team2 AND EXTRACT(YEAR FROM date) = $season)) p", vars=i)[0]
			team2ptsagainst = db.query("SELECT SUM(p.a) FROM (SELECT SUM(team1score) AS a FROM schedule WHERE (team2 = $team2 AND EXTRACT(YEAR FROM date) = $season) UNION ALL SELECT SUM(team2score) AS a FROM schedule WHERE (team1 = $team2 AND EXTRACT(YEAR FROM date) = $season)) p", vars=i)[0]
			team2gamesplayed = int(team2wins.count + team2losses.count + team2ties.count)
			team2pointslost = db.query("SELECT SUM(teamlines_points_lost) FROM schedule WHERE teamlines = $team2 AND EXTRACT(YEAR FROM date) = $season", vars=i)[0]
			if team2pointslost.sum is None:
				team2points = int(team2wins.count*2 + team2ties.count)
			else:
				team2points = int(team2wins.count*2 + team2ties.count - team2pointslost.sum)
			
			teamlineswins = db.query("SELECT COUNT(*) FROM schedule WHERE (team1score > team2score AND team1 = $teamlines AND EXTRACT(YEAR FROM date) = $season) OR (team2score > team1score AND team2 = $teamlines AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			teamlinesties = db.query("SELECT COUNT(*) FROM schedule WHERE (team2score = team1score AND team1 = $teamlines AND EXTRACT(YEAR FROM date) = $season) OR (team2score = team1score AND team2 = $teamlines AND EXTRACT(YEAR FROM date) = $season)", vars=i)[0]
			teamlinespointslost = db.query("SELECT SUM(teamlines_points_lost) FROM schedule WHERE teamlines = $teamlines AND EXTRACT(YEAR FROM date) = $season", vars=i)[0]
			if teamlinespointslost.sum is None:
				teamlinespoints = int(teamlineswins.count*2 + teamlinesties.count)
			else:
				teamlinespoints = int(teamlineswins.count*2 + teamlinesties.count - teamlinespointslost.sum)
			
			t1 = dict(shortname=i.team1, gamesplayed=team1gamesplayed, wins=team1wins.count, losses=team1losses.count, ties=team1ties.count, points=team1points, pointsfor=team1ptsfor.sum, pointsagainst=team1ptsagainst.sum, season=i.season)
			t2 = dict(shortname=i.team2, gamesplayed=team2gamesplayed, wins=team2wins.count, losses=team2losses.count, ties=team2ties.count, points=team2points, pointsfor=team2ptsfor.sum, pointsagainst=team2ptsagainst.sum, season=i.season)
			t3 = dict(shortname=i.teamlines, points=teamlinespoints, season=i.season)
			if game_data.gametype == "reg":
				db.update('standings', where="shortname = $shortname AND season = $season", vars=t1, **t1)
				db.update('standings', where="shortname = $shortname AND season = $season", vars=t2, **t2)
				db.update('standings', where="shortname = $shortname AND season = $season", vars=t3, **t3)
			raise web.seeother('/admin/gameselect')
		else:
			return "You do not have permission to make this request"

class standings:
	def GET(self):
		i = web.input(season=None)
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		if i.season is None:
			i.season = season_current.year
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_list = db.select('season', order="year DESC")
		standingsmen = db.select('standings', order="points DESC, gamesplayed, pointsagainst", where="league = 'Mens' AND season = $season", vars=i)
		standingswomen = db.select('standings', order="points DESC, gamesplayed, pointsagainst", where="league = 'Womens' AND season = $season", vars=i)
		scheduledb2 = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		
		points_lost = db.query("SELECT teamlines, sum(teamlines_points_lost) FROM schedule WHERE EXTRACT(YEAR FROM date) = $season GROUP BY teamlines", vars=i)
		
		mens_team = db.select('standings', i, what="shortname", where="league='Mens' AND season = $season", limit=1)[0]
		i.mensteam = mens_team.shortname
		womens_team = db.select('standings', i, what="shortname", where="league='Womens' AND season = $season", limit=1)[0]
		i.womensteam = womens_team.shortname
		mens_games = db.query("SELECT COUNT(*) FROM schedule WHERE (team1 = $mensteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg') OR (team2 = $mensteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg')", vars=i)[0]
		womens_games = db.query("SELECT COUNT(*) FROM schedule WHERE (team1 = $womensteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg') OR (team2 = $womensteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg')", vars=i)[0]
		season_displayed = db.select('season', i, where="year = $season")[0]
		
		teams_list = db.select('standings', j, order="league, shortname", where="season=$season").list()

		render = create_render(session.privilege)
		return render.standings(standingsmen, standingswomen, teamsdb, scheduledb, season_list, i.season, teams_list)

class schedule:
	def GET(self):
		i = web.input(season=None, gametype="reg")
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		if i.season is None:
			i.season = season_current.year
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_list = db.select('season', order="year DESC")
		scheduledb2 = db.select('schedule', order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = $gametype", vars=i).list()
		teams_list = db.select('standings', i, order="league, shortname", where="season=$season").list()
		render = create_render(session.privilege)
		return render.schedule(teamsdb, scheduledb, scheduledb2, season_list, i.season, i.gametype, teams_list)

class teams:
	def GET(self):
		i = web.input(teamid=None)
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		team1_data = db.select('standings', i, where="id = $teamid")[0]
		i.season = team1_data.season
		scheduledb2 = db.select('schedule', order="date, time", where="EXTRACT(YEAR FROM date) = $season", vars=i).list()
		statsdb = db.query("SELECT play.playerid, play.teamid, play.firstname, play.lastname, COALESCE(stats.gameplayed, 0) AS gameplayed, COALESCE(stats.touchdowns, 0) AS touchdowns, COALESCE(stats.tdpass, 0) AS tdpass, COALESCE(stats.oneconvert, 0) AS oneconvert, COALESCE(stats.twoconvert, 0) AS twoconvert, COALESCE(stats.rouge, 0) AS rouge, COALESCE(stats.safety, 0) AS safety, COALESCE(stats.interception, 0) AS interception, COALESCE(stats.sack, 0) AS sack FROM (SELECT st.playerid, sum(st.gameplayed) AS gameplayed, sum(st.touchdowns) AS touchdowns, sum(st.tdpass) AS tdpass, sum(st.oneconvert) AS oneconvert, sum(st.twoconvert) AS twoconvert, sum(st.rouge) AS rouge, sum(st.safety) AS safety, sum(st.interception) AS interception, sum(st.sack) AS sack FROM (SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.gameplayed, s.touchdowns, s.tdpass, s.oneconvert, s.twoconvert, s.rouge, s.safety, s.interception, s.sack FROM (SELECT stat.playerid, sum(stat.gameplayed) AS gameplayed, sum(stat.touchdowns) AS touchdowns, sum(stat.tdpass) AS tdpass, sum(stat.oneconvert) AS oneconvert, sum(stat.twoconvert) AS twoconvert, sum(stat.rouge) AS rouge, sum(stat.safety) AS safety, sum(stat.interception) AS interception, sum(stat.sack) AS sack FROM statistics stat, schedule sched WHERE stat.gameid=sched.gameid AND stat.season = $season AND sched.gametype = 'reg' GROUP BY stat.playerid) s, players p WHERE s.playerid = p.playerid AND p.teamid = $teamid UNION ALL SELECT playerid, teamid, firstname, lastname, null AS gameplayed, null AS touchdowns, null AS tdpass, null AS oneconvert, null AS twoconvert, null AS rouge, null AS safety, null AS interception, null AS sack FROM players WHERE teamid = $teamid AND season = $season) AS st GROUP BY st.playerid) stats, players play WHERE stats.playerid = play.playerid ORDER BY play.lastname, play.firstname;", vars=i)
		teams_list = db.select('standings', i, order="league, shortname", where="season=$season").list()
		
		i.league = team1_data.league
		i.team1 = team1_data.shortname
		
		if team1_data.gamesplayed == 0:
			team1_stats = None
		else:
			team1_stats = db.query("SELECT * FROM (SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.touchdownsagainst) AS touchdownsagainst, sum(j.tdpass) AS tdpass, sum(j.tdpassagainst) AS tdpassagainst, sum(j.oneconvert) AS oneconvert, sum(j.oneconvertagainst) AS oneconvertagainst, sum(j.twoconvert) AS twoconvert, sum(j.twoconvertagainst) AS twoconvertagainst, sum(j.rouge) AS rouge, sum(j.rougeagainst) AS rougeagainst, sum(j.safety) AS safety, sum(j.safetyagainst) AS safetyagainst, sum(j.interception) AS interception, sum(j.interceptionagainst) AS interceptionagainst, sum(j.sack) AS sack, sum(j.sackagainst) AS sackagainst FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, 0 AS touchdownsagainst, sum(i.tdpass) AS tdpass, 0 AS tdpassagainst, sum(i.oneconvert) AS oneconvert, 0 AS oneconvertagainst, sum(i.twoconvert) AS twoconvert, 0 AS twoconvertagainst, sum(i.rouge) AS rouge, 0 AS rougeagainst, sum(i.safety) AS safety, 0 AS safetyagainst, sum(i.interception) AS interception, 0 AS interceptionagainst, sum(i.sack) AS sack, 0 AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i GROUP BY i.teamname UNION SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname) v WHERE v.shortname = $team1;", vars=i)[0]
		
		team1_last_wins = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score > team2score AND team1 = $team1) OR (team1score < team2score AND team2 = $team1);", vars=i)[0]
		team1_last_losses = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score < team2score AND team1 = $team1) OR (team1score > team2score AND team2 = $team1);", vars=i)[0]
		team1_last_ties = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score = team2score AND team1 = $team1) OR (team1score = team2score AND team2 = $team1);", vars=i)[0]
		
		team1_last = dict(wins=team1_last_wins.count, losses=team1_last_losses.count, ties=team1_last_ties.count)
		
		team1_streak = db.select('schedule', i, order="date DESC", where="(team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL").list()

		render = create_render(session.privilege)
		return render.teams(i.teamid, teamsdb, team1_data, scheduledb, scheduledb2, statsdb, teams_list, team1_stats, team1_last, team1_streak)

class scores:
	def GET(self):
		i = web.input(week="1", season=None, gametype="reg")
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		if i.season is None:
			i.season = season_current.year
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_list = db.select('season', order="year DESC")
		scheduledb2 = db.select('schedule', i, where="week = $week AND EXTRACT(YEAR FROM date) = $season AND gametype = $gametype", order="date, time")
		#statsdb = db.query("SELECT a.playerid, a.firstname, a.lastname, sum(c.touchdowns * 6 + c.twoconvert * 2 + c.safety * 2 + c.oneconvert + c.rouge) AS points, sum(c.sack) AS sack, sum(c.interception) AS interception, sum(c.tdpass) AS tdpass FROM (SELECT p.week, p.gameid, s.playerid, s.gameplayed, s.touchdowns, s.tdpass, s.oneconvert, s.twoconvert, s.rouge, s.safety, s.interception, s.sack FROM (SELECT gameid, playerid, gameplayed, touchdowns, tdpass, oneconvert, twoconvert, rouge, safety, interception, sack FROM statistics WHERE season = $season) s, schedule p WHERE p.gameid = s.gameid AND p.week = $week AND EXTRACT(YEAR FROM date) = $season) c, players a WHERE a.playerid = c.playerid AND season = $season GROUP BY a.playerid", vars=i).list()

		footerdb = db.query("SELECT stats.playerid, play.firstname, play.lastname, play.teamname, stats.gameid, stats.touchdowns, stats.tdpass, stats.interception, stats.sack, sched.week, sched.team1, sched.team2 FROM statistics stats, schedule sched, players play WHERE stats.gameid = sched.gameid AND sched.week=$week AND play.playerid = stats.playerid AND stats.season=$season AND play.season=$season AND EXTRACT(YEAR FROM sched.date)=$season;", vars=i).list()
		standingsdb = db.select('standings', order="points DESC, gamesplayed, pointsagainst", where="season = $season", vars=i)
		
		week_num = db.query("SELECT MAX(week) FROM schedule where EXTRACT(YEAR FROM date) = $season AND gametype = $gametype;", vars=i)[0]
		post_week_list = db.query("SELECT DISTINCT week FROM schedule WHERE  EXTRACT(YEAR FROM date) = $season AND gametype = 'post' ORDER BY week;", vars=i).list()
		teams_list = db.select('standings', i, order="league, shortname", where="season=$season").list()
		render = create_render(session.privilege)
		return render.scores(i.week, scheduledb, scheduledb2, teamsdb, footerdb, standingsdb, week_num, season_list, i.season, i.gametype, post_week_list, teams_list)


class statistics:
	def GET(self):
		i = web.input(month=None, season=None, gametype="reg")
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		if i.season is None:
			i.season = season_current.year
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_list = db.select('season', order="year DESC")
		
		teamlistdb = db.select('standings', order="league, shortname", where="season = $season", vars=i).list()
		playersdb = db.query("SELECT p.playerid, p.firstname, p.lastname, p.teamname, p.teamid, t.league FROM players p, standings t WHERE p.teamname=t.shortname AND p.season=$season AND t.season=$season;", vars=i).list()
		if i.month is None:
			statsdb = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.gameplayed, s.touchdowns, s.tdpass, s.oneconvert, s.twoconvert, s.rouge, s.safety, s.interception, s.sack FROM (SELECT m.playerid, sum(m.gameplayed) AS gameplayed, sum(m.touchdowns) AS touchdowns, sum(m.tdpass) AS tdpass, sum(m.oneconvert) AS oneconvert, sum(m.twoconvert) AS twoconvert, sum(m.rouge) AS rouge, sum(m.safety) AS safety, sum(m.interception) AS interception, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND EXTRACT(YEAR FROM sched.date)=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p WHERE p.playerid = s.playerid AND p.season=$season;", vars=i).list()
			pointsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 10;", vars=i)
			sacksdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 10;", vars=i)
			interceptionsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 10;", vars=i)
			tdpsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 10;", vars=i)
			pointsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 10;", vars=i)
			sacksdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 10;", vars=i)
			interceptionsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 10;", vars=i)
			tdpsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 10;", vars=i)
			teamstatsdb = db.query("SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.tdpass) AS tdpass, sum(j.oneconvert) AS oneconvert, sum(j.twoconvert) AS twoconvert, sum(j.rouge) AS rouge, sum(j.safety) AS safety, sum(j.interception) AS interception, sum(j.sack) AS sack FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, sum(i.tdpass) AS tdpass, sum(i.oneconvert) AS oneconvert, sum(i.twoconvert) AS twoconvert, sum(i.rouge) AS rouge, sum(i.safety) AS safety, sum(i.interception) AS interception, sum(i.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND sched.gametype=$gametype) i GROUP BY i.teamname UNION ALL SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, 0 AS tdpass, 0 AS oneconvert, 0 AS twoconvert, 0 AS rouge, 0 AS safety, 0 AS interception, 0 AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND sched.gametype=$gametype) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION ALL SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, 0 AS tdpass, 0 AS oneconvert, 0 AS twoconvert, 0 AS rouge, 0 AS safety, 0 AS interception, 0 AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND sched.gametype=$gametype) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname;", vars=i).list()
		else:
			statsdb = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.gameplayed, s.touchdowns, s.tdpass, s.oneconvert, s.twoconvert, s.rouge, s.safety, s.interception, s.sack FROM (SELECT m.playerid, sum(m.gameplayed) AS gameplayed, sum(m.touchdowns) AS touchdowns, sum(m.tdpass) AS tdpass, sum(m.oneconvert) AS oneconvert, sum(m.twoconvert) AS twoconvert, sum(m.rouge) AS rouge, sum(m.safety) AS safety, sum(m.interception) AS interception, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND EXTRACT(YEAR FROM sched.date)=$season AND EXTRACT(MONTH FROM sched.date)=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p WHERE p.playerid = s.playerid AND p.season=$season;", vars=i).list()
			pointsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 10;", vars=i).list()
			sacksdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 10;", vars=i).list()
			interceptionsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 10;", vars=i).list()
			tdpsdbmen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Mens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 10;", vars=i).list()
			pointsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.points FROM (SELECT m.playerid, sum(m.touchdowns * 6 + m.twoconvert * 2 + m.safety * 2 + m.oneconvert + m.rouge) AS points FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY points DESC, lastname LIMIT 10;", vars=i).list()
			sacksdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.sack FROM (SELECT m.playerid, sum(m.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY sack DESC, lastname LIMIT 10;", vars=i).list()
			interceptionsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.interception FROM (SELECT m.playerid, sum(m.interception) AS interception FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY interception DESC, lastname LIMIT 10;", vars=i).list()
			tdpsdbwomen = db.query("SELECT p.playerid, p.teamid, p.firstname, p.lastname, s.tdpass FROM (SELECT m.playerid, sum(m.tdpass) AS tdpass FROM (SELECT * FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND (EXTRACT(YEAR FROM sched.date))=$season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) m GROUP BY playerid) s, players p, standings t WHERE p.playerid = s.playerid AND p.teamid = t.id AND t.league = 'Womens' AND p.season = $season AND t.season = $season ORDER BY tdpass DESC, lastname LIMIT 10;", vars=i).list()
			teamstatsdb = db.query("SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.tdpass) AS tdpass, sum(j.oneconvert) AS oneconvert, sum(j.twoconvert) AS twoconvert, sum(j.rouge) AS rouge, sum(j.safety) AS safety, sum(j.interception) AS interception, sum(j.sack) AS sack FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, sum(i.tdpass) AS tdpass, sum(i.oneconvert) AS oneconvert, sum(i.twoconvert) AS twoconvert, sum(i.rouge) AS rouge, sum(i.safety) AS safety, sum(i.interception) AS interception, sum(i.sack) AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) i GROUP BY i.teamname UNION ALL SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, 0 AS tdpass, 0 AS oneconvert, 0 AS twoconvert, 0 AS rouge, 0 AS safety, 0 AS interception, 0 AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION ALL SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, 0 AS tdpass, 0 AS oneconvert, 0 AS twoconvert, 0 AS rouge, 0 AS safety, 0 AS interception, 0 AS sack FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season AND (EXTRACT(MONTH FROM sched.date))=$month AND sched.gametype=$gametype) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname;", vars=i).list()
		month_list = db.query("SELECT DISTINCT (EXTRACT(MONTH FROM sched.date)) FROM statistics stat, schedule sched WHERE stat.gameid = sched.gameid AND stat.season = $season AND EXTRACT(YEAR FROM sched.date)=$season ORDER BY(EXTRACT(MONTH FROM sched.date));", vars=i).list()

		render = create_render(session.privilege)
		return render.statistics(i.month, statsdb, teamsdb, scheduledb, playersdb, pointsdbmen, sacksdbmen, interceptionsdbmen, tdpsdbmen, pointsdbwomen, sacksdbwomen, interceptionsdbwomen, tdpsdbwomen, teamstatsdb, month_list, teamlistdb, season_list, i.season, i.gametype)

class news:
	def GET(self):
		i = web.input(page=1)
		season_current = db.select('season', where="current = 't'")[0]
		i.season = season_current.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		
		i.pageoffset = (int(i.page) - 1) * 5
		newsdb = db.select('news', i, order="posted DESC", limit=5, offset="$pageoffset")
		totalposts = db.query("SELECT COUNT(*) FROM news;")[0]
		i.lastpage = int(math.ceil(int(totalposts.count)/5.0))
		
		render = create_render(session.privilege)
		return render.news(newsdb, teamsdb, scheduledb, i.page, i.lastpage)

class preview:
	def GET(self):
		i = web.input(gameid=None)
		if i.gameid is None:
			raise web.redirect('/')
		season_current = db.select('season', where="current = 't'")[0]
		i.season = season_current.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		
		game_data = db.select('schedule', i, where="gameid = $gameid")[0]
		i.team1 = game_data.team1
		i.team2 = game_data.team2
		if int(game_data.date.strftime('%Y')) != int(season_current.year):
			raise web.redirect('/')
		
		team1_data = db.select('standings', i, where="shortname = $team1 AND season = $season")[0]
		team2_data = db.select('standings', i, where="shortname = $team2 AND season = $season")[0]
		
		i.league = team1_data.league
		
		team1_stats = db.query("SELECT * FROM (SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.touchdownsagainst) AS touchdownsagainst, sum(j.tdpass) AS tdpass, sum(j.tdpassagainst) AS tdpassagainst, sum(j.oneconvert) AS oneconvert, sum(j.oneconvertagainst) AS oneconvertagainst, sum(j.twoconvert) AS twoconvert, sum(j.twoconvertagainst) AS twoconvertagainst, sum(j.rouge) AS rouge, sum(j.rougeagainst) AS rougeagainst, sum(j.safety) AS safety, sum(j.safetyagainst) AS safetyagainst, sum(j.interception) AS interception, sum(j.interceptionagainst) AS interceptionagainst, sum(j.sack) AS sack, sum(j.sackagainst) AS sackagainst FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, 0 AS touchdownsagainst, sum(i.tdpass) AS tdpass, 0 AS tdpassagainst, sum(i.oneconvert) AS oneconvert, 0 AS oneconvertagainst, sum(i.twoconvert) AS twoconvert, 0 AS twoconvertagainst, sum(i.rouge) AS rouge, 0 AS rougeagainst, sum(i.safety) AS safety, 0 AS safetyagainst, sum(i.interception) AS interception, 0 AS interceptionagainst, sum(i.sack) AS sack, 0 AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i GROUP BY i.teamname UNION SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname) v WHERE v.shortname = $team1;", vars=i)[0]
		team2_stats = db.query("SELECT * FROM (SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.touchdownsagainst) AS touchdownsagainst, sum(j.tdpass) AS tdpass, sum(j.tdpassagainst) AS tdpassagainst, sum(j.oneconvert) AS oneconvert, sum(j.oneconvertagainst) AS oneconvertagainst, sum(j.twoconvert) AS twoconvert, sum(j.twoconvertagainst) AS twoconvertagainst, sum(j.rouge) AS rouge, sum(j.rougeagainst) AS rougeagainst, sum(j.safety) AS safety, sum(j.safetyagainst) AS safetyagainst, sum(j.interception) AS interception, sum(j.interceptionagainst) AS interceptionagainst, sum(j.sack) AS sack, sum(j.sackagainst) AS sackagainst FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, 0 AS touchdownsagainst, sum(i.tdpass) AS tdpass, 0 AS tdpassagainst, sum(i.oneconvert) AS oneconvert, 0 AS oneconvertagainst, sum(i.twoconvert) AS twoconvert, 0 AS twoconvertagainst, sum(i.rouge) AS rouge, 0 AS rougeagainst, sum(i.safety) AS safety, 0 AS safetyagainst, sum(i.interception) AS interception, 0 AS interceptionagainst, sum(i.sack) AS sack, 0 AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i GROUP BY i.teamname UNION SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname) v WHERE v.shortname = $team2;", vars=i)[0]
		allteam_stats = db.query("SELECT v.shortname AS shortname, v.pointsfor AS pointsfor, v.pointsagainst AS pointsagainst, v.touchdowns AS touchdowns, v.touchdownsagainst AS touchdownsagainst, v.tdpass AS tdpass, v.tdpassagainst AS tdpassagainst, v.oneconvert AS oneconvert, v.oneconvertagainst AS oneconvertagainst, v.twoconvert AS twoconvert, v.twoconvertagainst AS twoconvertagainst, v.rouge AS rouge, v.rougeagainst AS rougeagainst, v.safety AS safety, v.safetyagainst AS safetyagainst, v.interception AS interception, v.interceptionagainst AS interceptionagainst, v.sack AS sack, v.sackagainst AS sackagainst , w.league AS league, w.gamesplayed AS gamesplayed FROM (SELECT j.teamname AS shortname, sum(j.pointsfor) AS pointsfor, sum(j.pointsagainst) AS pointsagainst, sum(j.touchdowns) AS touchdowns, sum(j.touchdownsagainst) AS touchdownsagainst, sum(j.tdpass) AS tdpass, sum(j.tdpassagainst) AS tdpassagainst, sum(j.oneconvert) AS oneconvert, sum(j.oneconvertagainst) AS oneconvertagainst, sum(j.twoconvert) AS twoconvert, sum(j.twoconvertagainst) AS twoconvertagainst, sum(j.rouge) AS rouge, sum(j.rougeagainst) AS rougeagainst, sum(j.safety) AS safety, sum(j.safetyagainst) AS safetyagainst, sum(j.interception) AS interception, sum(j.interceptionagainst) AS interceptionagainst, sum(j.sack) AS sack, sum(j.sackagainst) AS sackagainst FROM (SELECT i.teamname, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsfor, 0 AS pointsagainst, sum(i.touchdowns) AS touchdowns, 0 AS touchdownsagainst, sum(i.tdpass) AS tdpass, 0 AS tdpassagainst, sum(i.oneconvert) AS oneconvert, 0 AS oneconvertagainst, sum(i.twoconvert) AS twoconvert, 0 AS twoconvertagainst, sum(i.rouge) AS rouge, 0 AS rougeagainst, sum(i.safety) AS safety, 0 AS safetyagainst, sum(i.interception) AS interception, 0 AS interceptionagainst, sum(i.sack) AS sack, 0 AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i GROUP BY i.teamname UNION SELECT i.team1 AS team, 0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team1 != i.teamname GROUP BY i.team1 UNION SELECT i.team2 AS team ,0 AS pointsfor, sum(i.touchdowns * 6 + i.twoconvert * 2 + i.safety * 2 + i.oneconvert + i.rouge) AS pointsagainst, 0 AS touchdowns, sum(i.touchdowns) AS touchdownsagainst, 0 AS tdpass, sum (i.tdpass) AS tdpassagainst, 0 AS oneconvert, sum (i.oneconvert) AS oneconvertagainst, 0 AS twoconvert, sum (i.twoconvert) AS twoconvertagainst, 0 AS rouge, sum (i.rouge) AS rougeagainst, 0 AS safety, sum (i.safety) AS safetyagainst, 0 AS interception, sum(i.interception) AS interceptionagainst, 0 AS sack, sum(i.sack) AS sackagainst FROM (SELECT * FROM statistics stat, schedule sched, players play WHERE stat.gameid = sched.gameid AND stat.playerid = play.playerid AND stat.season = $season AND play.season = $season AND EXTRACT(YEAR FROM sched.date) = $season) i WHERE i.team2 != i.teamname GROUP BY i.team2) j GROUP BY j.teamname ORDER BY j.teamname) v, standings w WHERE v.shortname = w.shortname AND w.league = $league AND w.season = $season;", vars=i).list()
		
		team1_last_wins = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score > team2score AND team1 = $team1) OR (team1score < team2score AND team2 = $team1);", vars=i)[0]
		team1_last_losses = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score < team2score AND team1 = $team1) OR (team1score > team2score AND team2 = $team1);", vars=i)[0]
		team1_last_ties = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score = team2score AND team1 = $team1) OR (team1score = team2score AND team2 = $team1);", vars=i)[0]
		
		team2_last_wins = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team2 OR team2 = $team2) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score > team2score AND team1 = $team2) OR (team1score < team2score AND team2 = $team2);", vars=i)[0]
		team2_last_losses = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team2 OR team2 = $team2) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score < team2score AND team1 = $team2) OR (team1score > team2score AND team2 = $team2);", vars=i)[0]
		team2_last_ties = db.query("SELECT COUNT(*) FROM (SELECT * FROM schedule WHERE (team1 = $team2 OR team2 = $team2) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL ORDER BY date DESC LIMIT 5) AS a WHERE (team1score = team2score AND team1 = $team2) OR (team1score = team2score AND team2 = $team2);", vars=i)[0]
		
		team1_last = dict(wins=team1_last_wins.count, losses=team1_last_losses.count, ties=team1_last_ties.count)
		team2_last = dict(wins=team2_last_wins.count, losses=team2_last_losses.count, ties=team2_last_ties.count)
		
		team1_streak = db.select('schedule', i, order="date DESC", where="(team1 = $team1 OR team2 = $team1) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL").list()
		team2_streak = db.select('schedule', i, order="date DESC", where="(team1 = $team2 OR team2 = $team2) AND EXTRACT(YEAR FROM date) = $season AND team1score IS NOT NULL").list()
		
		render = create_render(session.privilege)
		return render.preview(teamsdb, scheduledb, game_data, team1_data, team2_data, team1_stats, team2_stats, allteam_stats, team1_last, team2_last, team1_streak, team2_streak)

class history:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i=dict(season = season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		
		championsdb = db.select('champions', order="year DESC")
		
		render = create_render(session.privilege)
		return render.history(teamsdb, scheduledb, championsdb)

class game:
	def GET(self):
		i = web.input(gameid=None)
		if i.gameid is None:
			raise web.redirect('/')
		season_current = db.select('season', where="current = 't'")[0]
		i.season = season_current.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		statsdb = db.select('statistics', i, where="gameid = $gameid AND season = $season")
		game_data = db.select('schedule', i, where="gameid = $gameid AND EXTRACT(YEAR FROM date) = $season")[0]
		playersdb = db.select('players', i, order="lastname, firstname", where="season = $season").list()

		i.team1 = game_data.team1
		i.team2 = game_data.team2
		team1_data = db.select('standings', i, where="shortname = $team1 AND season = $season")[0]
		team2_data = db.select('standings', i, where="shortname = $team2 AND season = $season")[0]

		render = create_render(session.privilege)
		return render.game(i.gameid, statsdb, teamsdb, scheduledb, game_data, playersdb, team1_data, team2_data)

class addgame:
	def GET(self):
		i = web.input(gameid=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i.season = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		statsdb = db.select('statistics', i, where="gameid = $gameid AND season = $season")
		game_data = db.select('schedule', i, where="gameid = $gameid AND EXTRACT(YEAR FROM date) = $season")[0]
		playersdb = db.select('players', i, order="lastname, firstname", where="season = $season").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.addgame(i.gameid, statsdb, teamsdb, scheduledb, game_data, playersdb)
		else:
			return "You do not have permission to access this page"
		
class teamselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		teamsdb2 = db.select('standings', order="id", where="season=$season", vars=i)
		render = create_render(session.privilege)
		if session.logged == True:
			return render.teamselect(scheduledb, teamsdb, teamsdb2)
		else:
			return "You do not have permission to access this page"

class teamedit:
	def GET(self):
		i = web.input(teamid=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i['season'] = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		teamsdb2 = db.select('standings', i, where="id = $teamid AND season = $season")
		leaguelist = db.query("SELECT DISTINCT league FROM standings;").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.teamedit(scheduledb, teamsdb, teamsdb2, leaguelist)
		else:
			return "You do not have permission to access this page"

class teameditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i['season'] = season.year
			db.update('standings', where="id = $id AND season = $season", vars=i, **i)
			team_players = db.select('players', i, where="teamid = $id AND season = $season")
			for player in team_players:
				t = dict(playerid=player.playerid, teamid=i.id, teamname=i.shortname)
				db.update('players', where="playerid = $playerid", vars=t, **t)
			raise web.seeother('/admin/teamselect')
		else:
			return "You do not have permission to make this request"

class teamadd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		leaguelist = db.query("SELECT DISTINCT league FROM standings;").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.teamadd(scheduledb, teamsdb, leaguelist)
		else:
			return "You do not have permission to access this page"

class teamaddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i['season'] = season.year
			db.insert('standings', name = i.name, shortname = i.shortname, league = i.league, season = i.season, gamesplayed = 0, wins = 0, losses = 0, ties = 0, points = 0, pointsfor = 0, pointsagainst = 0)
			raise web.seeother('/admin/teamselect')
		else:
			return "You do not have permission to make this request"

class teamdeletesubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i['season'] = season.year
			db.delete('standings', where="id = $id AND season = $season", vars=i)
			playersFA = db.select('players', i, where="teamid = $id AND season = $season")
			for player in playersFA:
				t = dict(playerid=player.playerid, teamid=0, teamname="Free Agent")
				db.update('players', where="playerid = $playerid", vars=t, **t)
			raise web.seeother('/admin/teamselect')
		else:
			return "You do not have permission to make this request"

class gameselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		scheduledb2 = db.select('schedule', order="date, time", where="EXTRACT(YEAR FROM date)=$season", vars=i)
		render = create_render(session.privilege)
		if session.logged == True:
			return render.gameselect(teamsdb, scheduledb, scheduledb2)
		else:
			return "You do not have permission to access this page"

class playerselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		playerdb = db.select('players', order="playerid", where="season=$season", vars=i)
		render = create_render(session.privilege)
		if session.logged == True:
			return render.playerselect(scheduledb, teamsdb, playerdb)
		else:
			return "You do not have permission to access this page"

class playeredit:
	def GET(self):
		i = web.input(playerid=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i['season'] = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		playerdb = db.select('players', i, where="playerid = $playerid").list()
		tdb = db.select('standings', i, order="league, shortname", where="season = $season").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.playeredit(scheduledb, teamsdb, playerdb, tdb)
		else:
			return "You do not have permission to access this page"

class playereditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i.season = season.year
			if i.teamname == "Free Agent":
				i.teamid = 0
			else:
				teamidnew = db.query("SELECT id FROM standings WHERE shortname = $teamname AND season = $season", vars=i).list()
				for team in teamidnew:
					teamidn = team.id
				i.teamid = teamidn
			db.update('players', where="playerid = $playerid AND season = $season", vars=i, **i)
			raise web.seeother('/admin/playerselect')
		else:
			return "You do not have permission to make this request"

class playeradd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		tdb = db.select('standings', i, order="league, shortname", where="season = $season").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.playeradd(scheduledb, teamsdb, tdb)
		else:
			return "You do not have permission to access this page"

class playeraddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i.season = season.year
			if i.teamname == "Free Agent":
				i.teamid = 0
			else:
				teamidnew = db.query("SELECT id FROM standings WHERE shortname = $teamname AND season = $season", vars=i).list()
				for team in teamidnew:
					teamidn = team.id
				i.teamid = teamidn
			db.insert('players', firstname = i.firstname, lastname = i.lastname, teamname = i.teamname, teamid = i.teamid, season = i.season)
			raise web.seeother('/admin/playerselect')
		else:
			return "You do not have permission to make this request"

class playerdeletesubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i.season = season.year
			db.delete('players', where="playerid = $playerid AND season = $season", vars=i)
			db.delete('statistics', where="playerid = $playerid AND season = $season", vars=i)
			raise web.seeother('/admin/playerselect')
		else:
			return "You do not have permission to make this request"

class scheduleselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		scheduledb2 = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season")
		render = create_render(session.privilege)
		if session.logged == True:
			return render.scheduleselect(teamsdb, scheduledb, scheduledb2)
		else:
			return "You do not have permission to access this page"

class scheduleedit:
	def GET(self):
		i = web.input(gameid=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i.season = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		game_data = db.select('schedule', i, where="gameid = $gameid AND EXTRACT(YEAR FROM date) = $season")[0]
		team_list = db.select('standings', i, order="id", where="season=$season").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.scheduleedit(scheduledb, teamsdb, game_data, team_list)
		else:
			return "You do not have permission to access this page"


class scheduleupload:
	def GET(self):
		i = web.input()
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i.season = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		render = create_render(session.privilege)
		if session.logged == True:
			return render.scheduleupload(teamsdb, scheduledb)
		else:
			return "You do not have permission to access this page"

class scheduleuploadsubmit:
	def POST(self):
		i = web.input(myfile={})
		if session.logged == True:
			filedir = os.environ.get('DATA_PATH')
			if 'myfile' in i: # to check if the file-object is created
				filepath=i.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				filename=filepath.split('/')[-1] # splits the path and chooses the last part (the filename with extension)
				fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
				fout.write(i.myfile.file.read()) # writes the uploaded file to the newly created file.
				fout.close() # closes the file, upload complete.
			filefull = str(filedir) +"/"+ str(filename)
			f = dict(file=filefull)
			db.query("COPY schedule (week, date, time, team1, team2, teamlines, gametype) FROM $file CSV", vars=f)
			db.query("SELECT setval('schedule_gameid_seq'::regclass, (SELECT MAX(gameid) FROM schedule)+1);")
			raise web.seeother('/admin/scheduleselect')
		else:
			return "You do not have permission to make this request"

class scheduleeditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.update('schedule', where="gameid = $gameid", vars=i, **i)
			raise web.seeother('/admin/scheduleselect')
		else:
			return "You do not have permission to make this request"

class scheduledeletesubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			season_current = db.select('season', where="current = 't'")
			for season in season_current:
				i.season = season.year
			db.delete('schedule', where="gameid = $gameid AND EXTRACT(YEAR FROM date) = $season", vars=i)
			db.delete('statistics', where="gameid = $gameid AND season=$season", vars=i)
			raise web.seeother('/admin/scheduleselect')
		else:
			return "You do not have permission to make this request"

class scheduleadd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		team_list = db.select('standings', i, order="league, shortname", where="season=$season").list()
		render = create_render(session.privilege)
		if session.logged == True:
			return render.scheduleadd(scheduledb, teamsdb, team_list)
		else:
			return "You do not have permission to access this page"

class scheduleaddsubmit:
	def POST(self):
		i = web.input(teamlines=None)
		if session.logged == True:
			if i.teamlines is None:	
				db.insert('schedule', week = i.week, date = i.date, time = i.time, team1 = i.team1, team2 = i.team2, gametype = i.gametype)
			else:
				db.insert('schedule', week = i.week, date = i.date, time = i.time, team1 = i.team1, team2 = i.team2, teamlines = i.teamlines, gametype = i.gametype)
			raise web.seeother('/admin/scheduleselect')
		else:
			return "You do not have permission to make this request"

class newsselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		newsdb = db.select('news', order="posted DESC")
		render = create_render(session.privilege)
		if session.logged == True:
			return render.newsselect(teamsdb, scheduledb, newsdb)
		else:
			return "You do not have permission to access this page"

class newsadd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		render = create_render(session.privilege)
		if session.logged == True:
			return render.newsadd(scheduledb, teamsdb)
		else:
			return "You do not have permission to access this page"

class newsaddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.insert('news', title = i.title, body = i.body, embed = i.embed)
			raise web.seeother('/admin/newsselect')
		else:
			return "You do not have permission to make this request"
		
class newsedit:
	def GET(self):
		i = web.input(id=None)
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i.season = season.year
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		post_data = db.select('news', i, where="id = $id")[0]
		render = create_render(session.privilege)
		if session.logged == True:
			return render.newsedit(scheduledb, teamsdb, post_data)
		else:
			return "You do not have permission to access this page"

class newseditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.update('news', where="id = $id", vars=i, **i)
			raise web.seeother('/admin/newsselect')
		else:
			return "You do not have permission to make this request"

class newsdeletesubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.delete('news', where="id = $id", vars=i)
			raise web.seeother('/admin/newsselect')
		else:
			return "You do not have permission to make this request"

class seasonselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")
		for season in season_current:
			i = dict(season=season.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		seasondb = db.select('season', order="year DESC")
		render = create_render(session.privilege)
		if session.logged == True and session.privilege == 1:
			return render.seasonselect(scheduledb, teamsdb, seasondb)
		else:
			return "You do not have permission to access this page"

class seasonedit:
	def GET(self):
		i = web.input(season=None)
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_data = db.select('season', i, where="year = $season")[0]
		render = create_render(session.privilege)
		if session.logged == True and session.privilege == 1:
			return render.seasonedit(scheduledb, teamsdb, season_data)
		else:
			return "You do not have permission to access this page"

class seasonadd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		season_list = db.select('season', order="year DESC")
		render = create_render(session.privilege)
		if session.logged == True and session.privilege == 1:
			return render.seasonadd(scheduledb, teamsdb, season_list)
		else:
			return "You do not have permission to access this page"
			
class seasonaddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True and session.privilege == 1:
			season_list = db.select('season')
			if i.current:
				for season in season_list:
					s = dict(id=season.id, current="f")
					db.update('season', where="id = $id", vars=s, **s)
			db.insert('season', year = i.year, current = i.current, playoff_teams_men = i.playoff_teams_men, playoff_teams_women = i.playoff_teams_women, bye_teams_men = i.bye_teams_men, bye_teams_women = i.bye_teams_women)
			db.query("INSERT INTO standings (name, shortname, league, season, color, sponsor_url, team_abbr, gamesplayed, wins, losses, ties, points, pointsfor, pointsagainst) SELECT name, shortname, league, $year, color, sponsor_url, team_abbr, 0, 0, 0, 0, 0, 0, 0 FROM standings AS old WHERE old.season = $prev;", vars=i)
			db.query("INSERT INTO players (firstname, lastname, teamname, teamid, season) SELECT p.firstname, p.lastname, p.teamname, t.id, $year FROM players p, standings t WHERE p.season = $prev AND p.teamname=t.shortname AND t.season = $year;", vars=i)
			raise web.seeother('/admin/seasonselect')
		else:
			return "You do not have permission to make this request"

class seasoneditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True and session.privilege == 1:
			db.update('season', where="id = $id", vars=i, **i)
			raise web.seeother('/admin/seasonselect')
		else:
			return "You do not have permission to make this request"
		
class seasoncurrentsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True and session.privilege == 1:
			season_current = db.query("SELECT id FROM season WHERE year = $year", vars=i).list()
			season_list = db.select('season')
			for season in season_list:
				s = dict(id=season.id, current="f")
				db.update('season', where="id = $id", vars=s, **s)
			for season in season_current:
				s = dict(id=season.id, current="t")
				db.update('season', where="id = $id", vars=s, **s)
			raise web.seeother('/admin/seasonselect')
		else:
			return "You do not have permission to make this request"

class historyselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		championsdb = db.select('champions', order="year DESC")

		render = create_render(session.privilege)
		if session.logged == True:
			return render.historyselect(scheduledb, teamsdb, championsdb)
		else:
			return "You do not have permission to access this page"

class historyadd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")

		render = create_render(session.privilege)
		if session.logged == True:
			return render.historyadd(scheduledb, teamsdb)
		else:
			return "You do not have permission to access this page"

class historyaddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.insert('champions', year = i.year, mens = i.champion_men, womens = i.champion_women)
			raise web.seeother('/admin/historyselect')
		else:
			return "You do not have permission to make this request"

class historyedit:
	def GET(self):
		i = web.input(season=None)
		season_current = db.select('season', where="current = 't'")[0]
		j = dict(season=season_current.year)
		teamsdb = db.select('standings', j, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', j, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		champion_data = db.select('champions', i, where="year = $season")[0]
		render = create_render(session.privilege)
		if session.logged == True:
			return render.historyedit(scheduledb, teamsdb, champion_data)
		else:
			return "You do not have permission to access this page"

class historyeditsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True:
			db.update('champions', where="id = $id", vars=i, **i)
			raise web.seeother('/admin/historyselect')
		else:
			return "You do not have permission to make this request"

class userselect:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")
		userdb = db.select('users')

		render = create_render(session.privilege)
		if session.logged == True and session.privilege == 1:
			return render.userselect(scheduledb, teamsdb, userdb)
		else:
			return "You do not have permission to access this page"

class useradd:
	def GET(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		teamsdb = db.select('standings', i, order="league, shortname", where="season=$season")
		scheduledb = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'")

		render = create_render(session.privilege)
		if session.logged == True and session.privilege == 1:
			return render.useradd(scheduledb, teamsdb)
		else:
			return "You do not have permission to access this page"

class useraddsubmit:
	def POST(self):
		i = web.input()
		if session.logged == True and session.privilege == 1:
			salt = bcrypt.gensalt()
			hashedpw = bcrypt.hashpw(i.password.encode('utf8'), salt)
			db.insert('users', username = i.username, password = hashedpw, email = i.email, privilege = i.privilege)
			raise web.seeother('/admin/userselect')
		else:
			return "You do not have permission to make this request"


class userdeletesubmit:
	def POST(self):
		i = web.input()
		if session.logged == True and session.privilege == 1:
			db.delete('users', where="id = $id", vars=i)
			raise web.seeother('/admin/userselect')
		else:
			return "You do not have permission to make this request"
		
class Edge(object):
	def __init__(self, u, v, w):
		self.source = u
		self.sink = v
		self.capacity = w
	def __repr__(self):
		return "%s->%s:%s" % (self.source, self.sink, self.capacity)

class FlowNetwork(object):
	def __init__(self):
		self.adj = {}
		self.flow = {}

	def add_vertex(self, vertex):
		self.adj[vertex] = []

	def get_edges(self, v):
		return self.adj[v]

	def add_edge(self, u, v, w=0):
		if u == v:
			raise ValueError("u == v")
		edge = Edge(u,v,w)
		redge = Edge(v,u,0)
		edge.redge = redge
		redge.redge = edge
		self.adj[u].append(edge)
		self.adj[v].append(redge)
		self.flow[edge] = 0
		self.flow[redge] = 0

	def find_path(self, source, sink, path):
		if source == sink:
			return path
		for edge in self.get_edges(source):
			residual = edge.capacity - self.flow[edge]
			if residual > 0 and edge not in path:
				result = self.find_path( edge.sink, sink, path + [edge])
				if result != None:
					return result

	def max_flow(self, source, sink):
		path = self.find_path(source, sink, [])
		while path != None:
			residuals = [edge.capacity - self.flow[edge] for edge in path]
			flow = min(residuals)
			for edge in path:
				self.flow[edge] += flow
				self.flow[edge.redge] -= flow
			path = self.find_path(source, sink, [])
		return sum(self.flow[edge] for edge in self.get_edges(source))


class maxflowsubmit:
	def POST(self):
		season_current = db.select('season', where="current = 't'")[0]
		i = dict(season=season_current.year)
		team_count = db.query("SELECT COUNT(*) FROM standings WHERE league = 'Mens' AND season = $season;", vars=i)[0]
		team_list = db.select('standings', order="points DESC, gamesplayed, pointsagainst", where="league = 'Mens' AND season = $season", vars=i).list()
		game_list = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season")
		
		games_rem_i_j = collections.defaultdict(lambda: collections.defaultdict(int))
		game_i_j = collections.defaultdict(lambda: collections.defaultdict(str))
		games_rem_k = collections.defaultdict(int)
		
		g = FlowNetwork()
		[g.add_vertex(v) for v in "sopqrt"]
		for team_k in team_list:
			for idx, team_i in enumerate(team_list, start=1):
				if team_i == team_k:
					continue
				for idx2, team_j in enumerate(team_list, start=1):
					if idx2 <= idx or team_j == team_k:
						continue
					for game in game_list:
						game_i_j[team_i.shortname][team_j.shortname] = team_i.shortname + team_j.shortname
						if (game.team1 == team_k.shortname or game.team1 == team_k.shortname) and (game.team1score is None):
							games_rem_k = 0
						if game.team1 == team_i.shortname and game.team2 == team_j.shortname and game.team1score is None:
							games_rem_i_j[team_i.shortname][team_j.shortname] += 1
						if game.team1 == team_j.shortname and game.team2 == team_i.shortname and game.team1score is None:
							games_rem_i_j[team_i.shortname][team_j.shortname] += 1
					g.add_edge('s',game_i_j[team_i.shortname][team_j.shortname],games_rem_i_j[team_i.shortname][team_j.shortname])
					g.add_edge(game_i_j[team_i.shortname][team_j.shortname],team_i.shortname,1)
					g.add_edge(game_i_j[team_i.shortname][team_j.shortname],team_j.shortname,1)
					team_k_capacity = team_k.wins+games_rem_k-team_i.wins
					g.add_edge(team_i.shortname,'t', team_k_capacity)
				
		#print (g.max_flow('s','t'))
		raise web.seeother('/standings')

def sort_standings(league_in, season_in):
	i = dict(season=season_in, league=league_in)
	standings_dict = db.select('standings', order="points DESC, gamesplayed, pointsagainst", where="league = $league AND season = $season", vars=i).list()
	sched_dict = db.select('schedule', i, order="date, time", where="EXTRACT(YEAR FROM date) = $season AND gametype = 'reg'").list()
	
	points_lost = db.query("SELECT teamlines, sum(teamlines_points_lost) FROM schedule WHERE EXTRACT(YEAR FROM date) = $season GROUP BY teamlines", vars=i)
	
	league_team = db.select('standings', i, what="shortname", where="league=$league AND season = $season", limit=1)[0]
	i['leagueteam'] = league_team.shortname
	league_games = db.query("SELECT COUNT(*) FROM schedule WHERE (team1 = $leagueteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg') OR (team2 = $leagueteam AND EXTRACT(YEAR FROM date) = $season AND gametype = 'reg')", vars=i)[0]
	season_displayed = db.select('season', i, where="year = $season")[0]

	
	# define empty dictionaries
	wins = collections.defaultdict(int)
	losses = collections.defaultdict(int)
	ties = collections.defaultdict(int)
	points = collections.defaultdict(int)
	games_played = collections.defaultdict(int)
	games_rem = collections.defaultdict(int)
	poss_points = collections.defaultdict(int)
	could_tie = collections.defaultdict(int)
	could_pass = collections.defaultdict(int)
	clinch = collections.defaultdict(str)
	penalty_symbol = collections.defaultdict(str)
	penalty_points = collections.defaultdict(int)
	
	# Define empty nested dictionaries for teams vs other teams
	hh_results = collections.defaultdict(lambda: collections.defaultdict(int))
	games_remaining_hh = collections.defaultdict(lambda: collections.defaultdict(int))
	could_tie_hh = collections.defaultdict(lambda: collections.defaultdict(int))
	
	# set total games remaining to 0 in case all games have been played
	total_games_rem = 0
	for team in points_lost:
		penalty_points[team.teamlines] = team.sum
		if team.sum >= 1:
			penalty_symbol[team.teamlines] = "*"


	# fill each team dictionary with team info from standings database
	for team in standings_dict:
		wins[team.shortname] = team.wins
		losses[team.shortname] = team.losses
		ties[team.shortname] = team.ties
		points[team.shortname] = team.points
		games_played[team.shortname] = team.wins + team.losses + team.ties
		games_rem[team.shortname] = league_games.count - (team.wins + team.losses + team.ties)
		poss_points[team.shortname] = team.points + games_rem[team.shortname] * 2
		total_games_rem += games_rem[team.shortname]
		team['points_lost'] = penalty_points[team.shortname]

	# fill nested dictionaries with head to head record vs every other team. Also fill if teams could tie in points, pass in points, or tie in head to head
	for team in standings_dict:
		for other_teams in standings_dict:
			if other_teams.shortname == team.shortname:
				 continue
			for game in sched_dict:
				if game.team1 == other_teams.shortname and game.team2 == team.shortname and game.team1score < game.team2score:
					hh_results[team.shortname][other_teams.shortname] += 1
				if game.team1 == other_teams.shortname and game.team2 == team.shortname and game.team1score > game.team2score:
					hh_results[team.shortname][other_teams.shortname] -= 1
				if game.team2 == other_teams.shortname and game.team1 == team.shortname and game.team2score < game.team1score:
					hh_results[team.shortname][other_teams.shortname] += 1
				if game.team2 == other_teams.shortname and game.team1 == team.shortname and game.team2score > game.team1score:
					hh_results[team.shortname][other_teams.shortname] -= 1
				if game.team2 == other_teams.shortname and game.team1 == team.shortname and game.team1score is None:
					games_remaining_hh[team.shortname][other_teams.shortname] += 1
				if game.team1 == other_teams.shortname and game.team2 == team.shortname and game.team1score is None:
					games_remaining_hh[team.shortname][other_teams.shortname] += 1
			if games_remaining_hh[team.shortname][other_teams.shortname] + hh_results[other_teams.shortname][team.shortname] >= 0:
				 could_tie_hh[team.shortname][other_teams.shortname] += 1
			
			if poss_points[other_teams.shortname] > points[team.shortname]:
				could_pass[team.shortname] += 1
			if poss_points[other_teams.shortname] == points[team.shortname] and could_tie_hh[team.shortname][other_teams.shortname] == 1:
				could_tie[team.shortname] += 1

	#define variables needed for head to head tiebreaker
	teams_tied = 0
	previous_team = None
	previous_team_points = None

	#this function is needed to calculate tiebreakers if there are more than 2 teams tied.
	for loop, team in enumerate(standings_dict):
		team['head_to_head'] = 0
		teamidx = loop
		if previous_team is None:
			previous_team = team.shortname
			previous_team_points = team.points
			continue
		elif team.points == previous_team_points:
			teams_tied = teams_tied + 1
			for s in range(teams_tied):
				idx = teamidx - (s + 1)
				tied_team = standings_dict[idx]['shortname']
				this_team = standings_dict[teamidx]['shortname']
				team['head_to_head'] += hh_results[team.shortname][tied_team]
				standings_dict[idx]['head_to_head'] += hh_results[tied_team][team.shortname]
		else:
			teams_tied = 0
		previous_team = team.shortname
		previous_team_points = team.points

	teams_tied = 0
	previous_team = None
	previous_team_points = None

	if league_in == 'Mens':
		playoff_teams = season_displayed.playoff_teams_men
		bye_teams = season_displayed.bye_teams_men
	elif league_in == 'Womens':
		playoff_teams = season_displayed.playoff_teams_women
		bye_teams = season_displayed.bye_teams_women

	#sort standings by points, points lost to penalty, head to head if ties, points against, pointsfor, name
	sorted_standings = multikeysort(standings_dict, ['-points', 'points_lost', '-head_to_head', 'pointsagainst', '-pointsfor', 'shortname'])
	#check to see if teams have clinched and add symbols if they have
	for loop, team in enumerate(sorted_standings, start=1):
		if could_pass[team.shortname] + could_tie[team.shortname] < playoff_teams:
			clinch[team.shortname] = "x -"
		if could_pass[team.shortname] + could_tie[team.shortname] < bye_teams:
			clinch[team.shortname] = "y -"
		if total_games_rem == 0 and loop <=  bye_teams and games_played[team.shortname] != 0:
			clinch[team.shortname] = "y -"

	return (sorted_standings, clinch, penalty_symbol)


def multikeysort(items, columns):
	#this is a function to sort dictionaries by multiple keys
	comparers = [((operator.itemgetter(col[1:].strip()), -1) if col.startswith('-') else
				(operator.itemgetter(col.strip()), 1)) for col in columns]
	def comparer(left, right):
		for fn, mult in comparers:
			result = cmp(fn(left), fn(right))
			if result:
				return mult * result
		else:
			return 0
	return sorted(items, cmp=comparer)

wsgiapp = app.wsgifunc()

if __name__ == "__main__":
	app.run()
