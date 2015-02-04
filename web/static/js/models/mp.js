var app = app || {};

app.Mp = Backbone.Model.extend({
    defaults: {
        image: 'none',
        name: 'No Name',
        party: 'Unknown',
        positions: 'None',
        register_of_interests_categories: 0,
        register_of_interests_count: 0,
        register_of_interests_relationships: 0,
        register_of_interests_total: 0,
        electoral_commission_count: 0,
        electoral_commission_total: 0,
        weight: 0
    }
});
