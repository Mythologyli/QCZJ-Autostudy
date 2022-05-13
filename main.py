import json
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from qczj import YouthLearning


def daka(nid, card_no, open_id, nickname, push_key, email=''):
    yl = YouthLearning(nid, card_no, open_id, nickname, push_key, email)
    yl.run()


if __name__ == '__main__':
    if os.path.exists('./users.json'):
        users = json.loads(open('./users.json', 'r').read())
    else:
        users = []

    for user in users:
        daka(user["nid"], user["cardNo"], user["openid"], user["nickname"], user["pushKey"], user["email"])

    scheduler = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})

    for user in users:
        scheduler.add_job(daka, 'cron',
                          args=[user["nid"], user["cardNo"], user["openid"], user["nickname"], user["pushKey"],
                                user["email"]],
                          hour=user["schedule"]["hour"], minute=user["schedule"]["minute"])

        print('已启动定时程序，每天 %02d:%02d 为您打卡' % (int(user["schedule"]["hour"]), int(user["schedule"]["minute"])))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
