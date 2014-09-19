;(function(undefined) {
  'use strict';

  sigma.classes.graph.addMethod('neighbors', function(nodeId) {
    var k,
        neighbors = {},
        index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
      neighbors[k] = this.nodesIndex[k];

    return neighbors;
  });

  sigma.utils.pkg('sigma.canvas.nodes');
  sigma.canvas.nodes.border = (function() {
    var _cache = {},
        _loading = {},
        _callbacks = {};

    // Return the renderer itself:
    var renderer = function(node, context, settings) {
      var args = arguments,
          prefix = settings('prefix') || '',
          size = node[prefix + 'size'],
          color = node.color || settings('defaultNodeColor'),
          border_color = node.border_color || settings('defaultNodeColor');

      // Draw the border:
      context.fillStyle = color;
      context.beginPath();
      context.arc(
        node[prefix + 'x'],
        node[prefix + 'y'],
        node[prefix + 'size'],
        0,
        Math.PI * 2,
        true
      );

      context.closePath();
      context.lineWidth = size / 8;
      context.strokeStyle = border_color;
      context.fill();        
      context.stroke();
    };
    return renderer;
  })();

}).call(this);

