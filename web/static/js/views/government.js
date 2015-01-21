var app = app || {};

app.GovernmentView = Backbone.View.extend({
    el: '#government-container',

    initialize: function() {
        this.collection = new app.Mps();
        this.collection.fetch();
        console.log(this.collection);
        this.render();

        this.listenTo( this.collection, 'add', this.renderMp );
        this.listenTo( this.collection, 'reset', this.render );
    },

    render: function() {
        this.collection.each(function( item ) {
            this.renderMp( item );
        }, this );
    },

    renderMp: function( item ) {
        var mpView = new app.MpView({
            model: item
        });
        this.$el.append( mpView.render().el );
    }
});
