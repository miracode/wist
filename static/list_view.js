$(document).ready(function(){
    $(".check-button").click(function(){
        $.ajax($SCRIPT_ROOT + '/lists/' + $(this).attr('data-list-id') + '/check', {
            type: 'POST',
            data: {item_id: $(this).attr('data-item-id')}
        }).done(function(){
            console.log('done')
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
