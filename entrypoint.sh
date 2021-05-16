#!/bin/bash
flask db upgrade
gunicorn