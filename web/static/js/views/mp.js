var app = app || {};

app.MpView = Backbone.View.extend({
    tagName: 'div',
    className: 'mp-container',
    template: _.template( $( '#mpTemplate' ).html() ),

    render: function() {
        //this.el is what we defined in tagName. use $el to get access to jQuery html() function
        this.$el.html( this.template( this.model.attributes ) );

        return this;
    }
});