function sortTable(columnIndex){
    const table = document.getElementById("p_list");
    const rows = Array.from(table.rows).slice(1); // skip header row
    const isAscending = table.getAttribute("data-sort-order") === "asc";
    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex].innerText.toLowerCase();
        const cellB = b.cells[columnIndex].innerText.toLowerCase();

        if (!isNaN(cellA) && !isNaN(cellB)) {
            return isAscending ? cellA - cellB : cellB - cellA;
        }
        return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });
    table.setAttribute("data-sort-order", isAscending ? "desc" : "asc");
    rows.forEach(row => table.tBodies[0].appendChild(row));
}

function hideOptions(e) {
    let divOptions = document.getElementById("divOptions");

    if (divOptions.contains(e.target)) {
        divOptions.style.display = "inline-block";
    } else {
        divOptions.style.display = "none";
    }
}

new MultiSelectTag('co', {
    rounded: true,    // default true
    shadow: true,      // default false
    placeholder: 'Search',  // default Search...
    tagColor: {
        textColor: '#1f6ff0',
        borderColor: '#d91434',
        bgColor: '#eaffe6',
    },
    onChange: function(values) {
        console.log(values)

    // Display the selected countries in the result paragraph
    document.getElementById('result').innerText = "Selected countries: " + values.join(", ");
    }
});

