$(document).ready(function(){
    $(".check-button").click(function(){
        var that = $(this)
        $.ajax($SCRIPT_ROOT + '/lists/' + that.attr('data-list-id') + '/check', {
            type: 'POST',
            data: {item_id: that.attr('data-item-id')}
        }).done(function(){
            state = that.attr('class').split(' ')[1]
            console.log(state)
            toggle(state, that)
        }).fail(function(){
            alert('everything died')
        })
    })

function toggle(state, object){
    if (state == 'check-button-0'){
        object.removeClass('check-button-0')
        object.addClass('check-button-1')
        object.siblings('p').addClass('strike')}
    else{
        object.removeClass('check-button-1')
        object.addClass('check-button-0')
        object.siblings('p').removeClass('strike')}
}
    // $(".check-button-1").click(function(){
    //     var that = $(this)
    //     var thatP = $(this).next('p')
    //     $.ajax($SCRIPT_ROOT + '/lists/' + that.attr('data-list-id') + '/check', {
    //         type: 'POST',
    //         data: {item_id: that.attr('data-item-id')}
    //     }).done(function(){
    //         that.removeClass('check-button-1')
    //         that.addClass('check-button-0')
    //         thatP.removeClass('strike')
    //     }).fail(function(){
    //         alert('everything died')
    //     })
    // })

    $(".delete-button").click(function(){
        var that = $(this)
        $.ajax($SCRIPT_ROOT + '/lists/' + $(this).attr('data-list-id') + '/remove', {
            type: 'POST',
            data: {item_id: $(this).attr('data-item-id')}
        }).done(function(){
            console.log(that.parent().closest('div').html())
            that.parent().parent().closest('div').html('')
        }).fail(function(){
            alert('everything died')
        })
    })

    $(".list-delete-button").click(function(){
        var that = $(this)
        $.ajax($SCRIPT_ROOT + '/lists/delete', {
            type: 'POST',
            data: {list_id: $(this).attr('data-list-id')}
        }).done(function(){
            console.log(that.parent().closest('div').html())
            that.parent().parent().closest('div').html('')
        }).fail(function(){
            alert('everything died')
        })
    })
})
