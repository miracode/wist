$(document).ready(function(){
    $(".check-button-0").click(function(){
        var that = $(this)
        var thatP = $(this).next('p')
        $.ajax($SCRIPT_ROOT + '/lists/' + that.attr('data-list-id') + '/check', {
            type: 'POST',
            data: {item_id: that.attr('data-item-id')}
        }).done(function(){
            that.css('background-color', '#00fc96')
            thatP.css('text-decoration', 'line-through')
        }).fail(function(){
            alert('everything died')
        })
    })

    $(".check-button-1").click(function(){
        var that = $(this)
        var thatP = $(this).next('p')
        $.ajax($SCRIPT_ROOT + '/lists/' + that.attr('data-list-id') + '/check', {
            type: 'POST',
            data: {item_id: that.attr('data-item-id')}
        }).done(function(){
            that.css('background-color', 'azure')
            thatP.removeClass('strike')
        }).fail(function(){
            alert('everything died')
        })
    })

    $(".delete-button").click(function(){
        $.ajax($SCRIPT_ROOT + '/lists/' + $(this).attr('data-list-id') + '/remove', {
            type: 'POST',
            data: {item_id: $(this).attr('data-item-id')}
        }).done(function(){
            alert('you deleted a thing')
        }).fail(function(){
            alert('everything died')
        })
    })

    $(".list-delete-button").click(function(){
        $.ajax($SCRIPT_ROOT + '/lists/delete', {
            type: 'POST',
            data: {list_id: $(this).attr('data-list-id')}
        }).done(function(){
            alert('you deleted a thing')
        }).fail(function(){
            alert('everything died')
        })
    })
})
