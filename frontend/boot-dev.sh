#!/bin/sh
: "${PORT:-80}"

yarn
exec yarn start
