new MultiSelectTag('color', {
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
