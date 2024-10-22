#!/bin/bash

usage() {
  cat <<EOF
Usage: ${0} [options]

-h, --help         Display this help message
-a, --api-url      API URL (default: http://127.0.0.1:9906)
-u, --username     Username for login (default: root)
-p, --password     Password for login (default: toor)
-d, --images-dir   Directory containing the images to upload (default: collected-images)

Examples:

${0} -u myuser -p mypass -d /path/to/images
${0} --help
EOF
  exit 1
}

api_url="http://127.0.0.1:9906"
username="root"
password="toor"
images_dir="collected-images"

while [[ "${#}" -gt 0 ]]; do
  case "${1}" in
  -h | --help)
    usage
    ;;
  -a | --api-url)
    api_url="${2}"
    shift 2
    ;;
  -u | --username)
    username="${2}"
    shift 2
    ;;
  -p | --password)
    password="${2}"
    shift 2
    ;;
  -d | --images-dir)
    images_dir="${2}"
    shift 2
    ;;
  *)
    echo "Unknown option: ${1}"
    usage
    ;;
  esac
done

if [ ! -d "${images_dir}" ]; then
  echo "Error: Images directory does not exist."
  exit 1
fi

if [ -f "cookies.txt" ]; then
  echo "Cookie file exists, skipping login..."
else
  curl -X POST \
    "${api_url}/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${username}\", \"password\": \"${password}\"}" \
    -c cookies.txt

  if [ ! -f "cookies.txt" ]; then
    echo "Error: Login failed. No cookies saved."
    exit 1
  fi
fi

for image in "${images_dir}"/*; do
  echo
  if [ -f "${image}" ]; then
    curl -X POST \
      "${api_url}/images/" \
      -F "media_file=@${image}" \
      -b cookies.txt
    echo "Image uploaded: ${image}"
  fi
done

# rm cookies.txt
