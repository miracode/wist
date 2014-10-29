$(document).ready(function(){
    $(".check-button").click(function(){
        $.ajax($SCRIPT_ROOT + '/lists/' + $(this).attr('data-list-id') + '/check', {
            type: 'POST',
            data: {item_id: $(this).attr('data-item-id')}
        }).done(function(){
            console.log($(this).attr('data-item-id'))
            alert('checked! Things are awesome.')
        }).fail(function(){
            alert('everything died')
        })
    })
})
