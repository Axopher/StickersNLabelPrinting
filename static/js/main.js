function handleLabelTypeChange() {
    var entireSheetLabel = document.getElementById("entire-sheet-label");
    var rowsColumnsLabel = document.getElementById("rows-columns-label");
    
    var entireSheetDropdown = document.getElementById("entire-sheet-dropdown");
    var rowsDropdown = document.getElementById("rows-dropdown");
    var columnsDropdown = document.getElementById("columns-dropdown");

    var selectedLabel = document.getElementById("selectedLabel");

    entireSheetDropdown.disabled = !entireSheetLabel.checked;
    selectedLabel.disabled = entireSheetLabel.checked;
    rowsDropdown.disabled = entireSheetLabel.checked;
    columnsDropdown.disabled = entireSheetLabel.checked;


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

    
    var index = Number(selectedLabel.value)
    console.log(index)

    
    // Clear existing options
    rowsDropdown.innerHTML = "";
    columnsDropdown.innerHTML = "";
    
    // Add new options
    var rowsOptions = Array.from({ length: dictionary[index]['rows'] }, (_, i) => i + 1);
    
    // or alternatively,
    // var rowsOptions = [];
    // var rowCount = dictionary[index]['rows'];
      
    // for (var i = 1; i <= rowCount; i++) {
    //     rowsOptions.push(i);
    // }
    
    var columnsOptions = Array.from({ length: dictionary[index]['columns'] }, (_, i) => i + 1);
    

    for (var i = 0; i < rowsOptions.length; i++) {
        var option = document.createElement("option");
        option.value = rowsOptions[i];
        option.text = rowsOptions[i];
        rowsDropdown.appendChild(option);
    }
    
    for (var i = 0; i < columnsOptions.length; i++) {
        var option = document.createElement("option");
        option.value = columnsOptions[i];
        option.text = columnsOptions[i];
        columnsDropdown.appendChild(option);
    }
        
    // Add an event listener to the form submission event
    document.getElementById("submit-btn").addEventListener("click", function(event) {
        // Enable the dropdown fields before submitting the form
        document.getElementById("rows-dropdown").disabled = false;
        document.getElementById("columns-dropdown").disabled = false;
    });

}

