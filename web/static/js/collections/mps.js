var app = app || {};

app.Mps = Backbone.Collection.extend({
    model: app.Mp,
    url: '/api/v0.1/mps'
});

