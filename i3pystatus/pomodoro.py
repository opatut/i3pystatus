#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import locale

from datetime import datetime, timedelta

from i3pystatus import IntervalModule


class Pomodoro(IntervalModule):
  """
  This plugin shows Pomodoro timer.

  Left click starts/restarts timer.
  Right click stops it.
  """

  settings = (
    ('sound', 'Path to sound file to play as alarm. Played by "aplay" utility'),
    ('pomodoro_duration', 'Working (pomodoro) interval duration in seconds'),
    ('break_duration', 'Short break duration in secods'),
    ('long_break_duration', 'Long break duration in secods'),
    ('short_break_count', 'Short break count before first long break'),
  )

  color_stopped = '#2ECCFA'
  color_running = '#FFFF00'
  color_break = '#37FF00'
  interval = 1
  short_break_count = 3

  pomodoro_duration = 25 * 60
  break_duration = 5 * 60
  long_break_duration = 15 * 60

  def init(self):
    # state could be either running/break or stopped
    self.state = 'stopped'
    self.breaks = 0
    self.time = None

  def run(self):
    if self.time and datetime.now() >= self.time:
      if self.state == 'running':
        self.state = 'break'
        if self.breaks == self.short_break_count:
          self.time = datetime.now() + timedelta(seconds=self.long_break_duration)
          self.breaks = 0
        else:
          self.time = datetime.now() + timedelta(seconds=self.break_duration)
        text = 'Go for a break!'
        self.breaks += 1
      else:
        self.state = 'running'
        self.time = datetime.now() + timedelta(seconds=self.pomodoro_duration)
        text = 'Back to work!'
      self._alarm(text)

    if self.state == 'running' or self.state == 'break':
      min, sec = divmod((self.time - datetime.now()).total_seconds(), 60)
      text = '{:02}:{:02}'.format(int(min), int(sec))
      color = self.color_running if self.state == 'running' else self.color_break
    else:
      text = 'Stopped'
      color = self.color_stopped

    self.output = {
        'full_text': text,
        'color': color
    }

  def on_leftclick(self):
    self.state = 'running'
    self.time = datetime.now() + timedelta(seconds=self.pomodoro_duration)

  def on_rightclick(self):
    self.state = 'stopped'
    self.time = None

  def _alarm(self, text):
    subprocess.call(['notify-send',
                      'Alarm!',
                      text])
    subprocess.Popen(['aplay',
                      self.sound,
                      '-q'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

