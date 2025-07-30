#include <iostream>
using namespace std;

int main() {
    // Print a welcome message
    cout << "Welcome to the C++ sample program!" << endl;

    // Declare variables
    int number;

    // Get user input
    cout << "Enter a number: ";
    cin >> number;

    // Conditional check
    if (number % 2 == 0) {
        cout << number << " is even." << endl;
    } else {
        cout << number << " is odd." << endl;
    }

    // Loop example
    cout << "Counting from 1 to " << number << ":" << endl;
    for (int i = 1; i <= number; i++) {
        cout << i << " ";
    }
    cout << endl;

    return 0;
}
