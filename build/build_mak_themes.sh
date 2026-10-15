#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MACTAHOE_DIR="$REPO_DIR/build/MacTahoe-gtk-theme"
STAGE_DIR="/tmp/mak_build_stage"

ACCENTS="${1:-all}"

echo "=== Building Mak themes using MacTahoe engine (accents: $ACCENTS) ==="
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

# 1. Dark Solid
echo "-> Building Dark Solid..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac" -t "$ACCENTS" -c dark -o solid --round >/dev/null

# 2. Dark Glassy (blur)
echo "-> Building Dark Glassy..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac" -t "$ACCENTS" -c dark -o normal -b --round >/dev/null

# 3. Light Solid
echo "-> Building Light Solid..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac" -t "$ACCENTS" -c light -o solid --round >/dev/null

# 4. Light Glassy (blur)
echo "-> Building Light Glassy..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac" -t "$ACCENTS" -c light -o normal -b --round >/dev/null

# 5. AMOLED Solid
echo "-> Building AMOLED Solid..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac-Dark-Amoled" -t "$ACCENTS" -c dark -o solid --darker --round >/dev/null

# 6. AMOLED Glassy (blur)
echo "-> Building AMOLED Glassy..."
"$MACTAHOE_DIR/install.sh" -d "$STAGE_DIR" -n ">>>Mac-Dark-Amoled" -t "$ACCENTS" -c dark -o normal --darker -b --round >/dev/null

# Remove hdpi / xhdpi duplicates to keep it clean and fast
rm -rf "$STAGE_DIR"/*-hdpi "$STAGE_DIR"/*-xhdpi

# Rename to standard Mak theme naming conventions
echo "-> Normalizing Mak theme names..."
cd "$STAGE_DIR"
for dir in *; do
    [ -d "$dir" ] || continue
    newdir="$dir"
    
    # Handle Dark glassy: '>>>Mac-Dark-<accent>' -> '>>>Mac-Dark-glassy-<accent>'
    if [[ "$newdir" =~ ^\>\>\>Mac-Dark-([a-zA-Z0-9]+)$ ]]; then
        accent="${BASH_REMATCH[1]}"
        if [ "$accent" != "solid" ]; then
            newdir=">>>Mac-Dark-glassy-$accent"
        fi
    fi
    
    # Handle Light glassy: '>>>Mac-Light-<accent>' -> '>>>Mac-Light-glassy-<accent>'
    if [[ "$newdir" =~ ^\>\>\>Mac-Light-([a-zA-Z0-9]+)$ ]]; then
        accent="${BASH_REMATCH[1]}"
        if [ "$accent" != "solid" ]; then
            newdir=">>>Mac-Light-glassy-$accent"
        fi
    fi
    
    # Handle AMOLED Solid: '>>>Mac-Dark-Amoled-Dark-solid-<accent>' -> '>>>Mac-Dark-Amoled-<accent>'
    if [[ "$newdir" =~ ^\>\>\>Mac-Dark-Amoled-Dark-solid-([a-zA-Z0-9]+)$ ]]; then
        accent="${BASH_REMATCH[1]}"
        newdir=">>>Mac-Dark-Amoled-$accent"
    fi
    
    # Handle AMOLED Glassy: '>>>Mac-Dark-Amoled-Dark-([a-zA-Z0-9]+)$' -> '>>>Mac-Dark-Amoled-glassy-<accent>'
    if [[ "$newdir" =~ ^\>\>\>Mac-Dark-Amoled-Dark-([a-zA-Z0-9]+)$ ]]; then
        accent="${BASH_REMATCH[1]}"
        newdir=">>>Mac-Dark-Amoled-glassy-$accent"
    fi
    
    if [ "$dir" != "$newdir" ]; then
        mv "$dir" "$newdir"
    fi
done

echo "=== Build Complete in $STAGE_DIR ==="
ls -1 "$STAGE_DIR"
