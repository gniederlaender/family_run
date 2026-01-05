#!/bin/bash
# Script to properly restart the Family Run application with updated PM2 configuration

echo "Stopping family-run application..."
pm2 stop family-run

echo "Deleting family-run from PM2..."
pm2 delete family-run

echo "Starting family-run with new configuration..."
pm2 start /opt/family_run/ecosystem.config.js

echo "Saving PM2 configuration..."
pm2 save

echo "Done! Application restarted with updated configuration."
pm2 list
