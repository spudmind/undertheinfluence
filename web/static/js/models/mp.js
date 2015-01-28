var app = app || {};

app.Mp = Backbone.Model.extend({
    defaults: {
        image: 'none',
        name: 'No Name',
        party: 'Unknown',
        positions: 'None',
        weight: 0
    }
});