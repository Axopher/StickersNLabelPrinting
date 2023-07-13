var entireSheetLabel = document.getElementById("entire-sheet-label");
var rowsColumnsLabel = document.getElementById("rows-columns-label");

var entireSheetDropdown = document.getElementById("entire-sheet-dropdown");
var starting_cell_number = document.getElementById("starting_cell_number");
var ending_cell_number = document.getElementById("ending_cell_number");

var selectedLabel = document.getElementById("selectedLabel");


var dictionary = {
    1: {
        'rows': 1,
        'columns': 1
    },
    2: {
        'rows': 2,
        'columns': 1
    },
    4: {
        'rows': 2,
        'columns': 2
    },
    6: {
        'rows': 3,
        'columns': 2
    },
    8: {
        'rows': 4,
        'columns': 2
    },
    10: {
        'rows': 5,
        'columns': 2
    },
    12: {
        'rows': 6,
        'columns': 2
    },
    14: {
        'rows': 7,
        'columns': 2
    },
    16: {
        'rows': 8,
        'columns': 2
    },
    18: {
        'rows': 6,
        'columns': 3
    },
    20: {
        'rows': 10,
        'columns': 2
    },
    21: {
        'rows': 7,
        'columns': 3
    },
    24: {
        'rows': 8,
        'columns': 3
    },
    30: {
        'rows': 6,
        'columns': 5
    },
    33: {
        'rows': 11,
        'columns': 3
    },
    40: {
        'rows': 10,
        'columns': 4
    },
    48: {
        'rows': 12,
        'columns': 4
    },
     56: {
        'rows': 14,
        'columns': 4
    },
    65: {
        'rows': 13,
        'columns': 5
    },
    84: {
        'rows': 21,
        'columns': 4
    }
};


function handleLabelTypeChange() {

    entireSheetDropdown.disabled = !entireSheetLabel.checked;
    selectedLabel.disabled = entireSheetLabel.checked;
    starting_cell_number.disabled = entireSheetLabel.checked;
    ending_cell_number.disabled = entireSheetLabel.checked;

    
    var index = Number(selectedLabel.value)

    // Clear existing options
    starting_cell_number.innerHTML = "";
    ending_cell_number.innerHTML = "";
    
    // Calculate the total number of cells
    var totalCells = dictionary[index]['rows'] * dictionary[index]['columns'];

    // Add options for rows
    for (var i = 1; i <= totalCells; i++) {
      var option = document.createElement("option");
      option.value = i;
      option.text = i;
      starting_cell_number.appendChild(option);
    }   

    // Add options for columns starting from the selected cell number option
    for (var i = 1; i <= totalCells; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = i;
        ending_cell_number.appendChild(option);
      }

}

function handleCellNumberChange(){
    console.log(starting_cell_number.value)
    var index = Number(selectedLabel.value)

    // Calculate the total number of cells
    var totalCells = dictionary[index]['rows'] * dictionary[index]['columns'];
    // Get the selected row option
    var selectedStartingCell = Number(starting_cell_number.value);
    ending_cell_number.innerHTML = "";

    // Add options for columns starting from the selected cell number option
    for (var i = selectedStartingCell; i <= totalCells; i++) {
      var option = document.createElement("option");
      option.value = i;
      option.text = i;
      ending_cell_number.appendChild(option);
    }

}
