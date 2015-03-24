// custom javascript


$(function() {
    createGraph();
});

function createGraph() {
    var width = 400; // chart width
    var height = 400; // chart height
    var format = d3.format(",d");  // convert value to integer
    var color = d3.scale.category20();  // create ordinal scale with 20 colors
    var sizeOfRadius = d3.scale.pow().domain([-100,100]).range([-50,50]);

    var bubble = d3.layout.pack()
        .sort(null)  // disable sorting, use DOM tree traversal
        .size([width, height])  // chart layout size
        .padding(1)  // padding between circles
        .radius(function(d) {
            console.dir(d);
            return 20 + (sizeOfRadius(d) * 120); });  // radius for each circle

    var svg = d3.select("#chart").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("class", "bubble");

    d3.json(
        "http://127.0.0.1:5000/data.json",
        function(error, donations) {
            var node = svg.selectAll('.node')
                .data(bubble.nodes(donations)
                    .filter(function(d) { return !d.children; }))
                .enter().append('g')
                .attr('class', 'node')
                .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'});

            node.append('circle')
                .attr('r', function(d) { return d.r; })
                .style('fill', function(d) { return color(d.name); });

            node.append('text')
                .attr("dy", ".3em")
                .style('text-anchor', 'middle')
                .text(function(d) { return d.name; });
        });

    // tooltip config
    var tooltip = d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden")
        .style("color", "white")
        .style("padding", "8px")
        .style("background-color", "rgba(0, 0, 0, 0.75)")
        .style("border-radius", "6px")
        .style("font", "12px sans-serif")
        .text("tooltip");

}


