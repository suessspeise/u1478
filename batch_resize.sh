# resizes images and leaves them in an subdirectory

# TO DO:
#	include making output for markdown 

# abort if no/too many arguments are given
if [ $# -ne 0 ]
then 
	echo "No paramters needed."
	echo "Should be executed from script directory"
	exit 0
fi

# directorys
web_image_dir="../img"
raw_image_dir="../original_images"

# give time estimate
FILECOUNT=$(echo "$(find $raw_image_dir -type f -name "*.png"| wc -l)" )
FILEMINUS=$(echo "$(find $web_image_dir -type f -name "*.png" | wc -l)" )
#FILEMINUS=$(echo "$FILEMINUS" | bc)
# experimental value from single_convert.sh: ~0.55 seconds
# * 2 conversions per file * number of files / 60 (s/min) 
differ=$(echo "$FILECOUNT - $FILEMINUS" | bc) 
dur=$(echo "$differ * 0.55 / 60.0" | bc)

echo "$differ files to convert (will take roughly $dur minutes)"
echo ""


# function, that resizes all images in one directory, stores them in directory according to their new resolution 
create_set()
{
	SIZE=$2
	DIR_FROM=$1
	DIR_TO="$SIZE/$(basename $1)"
	DIR_TO="$web_image_dir/$(basename $1)"
	echo "$DIR_TO"

	# make subdirectory
	mkdir -p "$DIR_TO"

	# convert images
	for file in $DIR_FROM/*.png
	do
		# only do if $file is file (no check for data type!)
		if [ -f "$file" ]; 	then
			if [ -s "$DIR_TO/$(basename "$file")" ]; then
				echo "$DIR_TO/$(basename "$file") already exists"
			else
				# getting the number out of the filname and using it as new filename
				newfilename="$(echo "$(basename "$file")"| tr "-" " ")" # replace "-" with " "
				nameparts=($newfilename) # make it an array
				newfilename="${nameparts[1]}.png" # use second array entry (filenames are something like this: "Snap-1660-Image Export-26.png"
				# just telling whats happening
				echo "$file to $DIR_TO/$newfilename"
				# to check if working comment out following line
				convert "$file" -resize $SIZE "$DIR_TO/$newfilename"
			fi
		fi
	done
	echo ""
}


# Conversion
for file in $raw_image_dir/*
	do
		# only do if $file is directory
		if [ -d "$file" ]; then
			#echo "Starting 300x150 for directory: $file"
			#create_set "$file" "300x150"
			echo "Starting 800x600 for directory: $file"
			create_set "$file" "800x600"
		fi
	done

# produce lists


# it has been a pleasure to resize your images
echo "done"
