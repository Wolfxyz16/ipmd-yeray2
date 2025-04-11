echo "Downloading zip data..."
wget --output-document=data.zip --quiet --show-progress https://ehubox.ehu.eus/s/6Rrwbt9gS2ZwXcY/download
echo "Unziping data"
unzip -q data.zip
rm data.zip
echo "Done!"
