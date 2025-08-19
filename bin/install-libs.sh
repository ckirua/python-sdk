# Install libzip-dev
if ! dpkg -s libzip-dev &> /dev/null; then
    echo "libzip-dev not found. Installing libzip-dev..."
    sudo apt-get update
    sudo apt-get install -y libzip-dev
else
    echo "libzip-dev is already installed."
fi  

# Install pybind11
if ! dpkg -s pybind11 &> /dev/null; then
    echo "pybind11 not found. Installing pybind11..."
    sudo apt-get update
    sudo apt-get install -y pybind11-dev
else
    echo "pybind11 is already installed."
fi
